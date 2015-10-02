#!/usr/bin/env python
"""
The SFTP server that acts as a reverse proxy
"""
import base64, os, fcntl, tty, struct

from twisted.enterprise import adbapi
import logging

from twisted.cred import portal, checkers, credentials
from twisted.conch import error, avatar
from twisted.conch.unix import SSHSessionForUnixConchUser,UnixConchUser, SFTPServerForUnixConchUser, UnixSFTPDirectory, UnixSFTPFile
from twisted.conch.checkers import SSHPublicKeyDatabase
from twisted.conch.ssh import factory, userauth, connection, keys, session
from twisted.internet import reactor, protocol, defer, task
from twisted.internet.defer import inlineCallbacks
from twisted.python import log
from zope.interface import implements
from twisted.python import components, failure
from twisted.conch.ssh import session, forwarding, filetransfer
from pysftpproxy.client import SFTPServerProxyClient
from twisted.internet.protocol import Protocol, ReconnectingClientFactory
from twisted.conch.ls import lsLine

import sys

#TODO, has to be changed
publicKey  = 'ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAGEArzJx8OYOnJmzf4tfBEvLi8DVPrJ3/c9k2I/Az64fxjHf9imyRJbixtQhlH9lfNjUIx+4LmrJH5QNRsFporcHDKOTwTTYLh5KmRpslkYHRivcJSkbh/C+BR3utDS555mV'

privateKey = """-----BEGIN RSA PRIVATE KEY-----
MIIByAIBAAJhAK8ycfDmDpyZs3+LXwRLy4vA1T6yd/3PZNiPwM+uH8Yx3/YpskSW
4sbUIZR/ZXzY1CMfuC5qyR+UDUbBaaK3Bwyjk8E02C4eSpkabJZGB0Yr3CUpG4fw
vgUd7rQ0ueeZlQIBIwJgbh+1VZfr7WftK5lu7MHtqE1S1vPWZQYE3+VUn8yJADyb
Z4fsZaCrzW9lkIqXkE3GIY+ojdhZhkO1gbG0118sIgphwSWKRxK0mvh6ERxKqIt1
xJEJO74EykXZV4oNJ8sjAjEA3J9r2ZghVhGN6V8DnQrTk24Td0E8hU8AcP0FVP+8
PQm/g/aXf2QQkQT+omdHVEJrAjEAy0pL0EBH6EVS98evDCBtQw22OZT52qXlAwZ2
gyTriKFVoqjeEjt3SZKKqXHSApP/AjBLpF99zcJJZRq2abgYlf9lv1chkrWqDHUu
DZttmYJeEfiFBBavVYIF1dOlZT0G8jMCMBc7sOSZodFnAiryP+Qg9otSBjJ3bQML
pSTqy7c3a2AScC/YyOwkDaICHnnD3XyjMwIxALRzl0tQEKMXs6hH8ToUdlLROCrP
EhQ0wahUTCk1gKA4uPD6TMTChavbh4K63OvbKg==
-----END RSA PRIVATE KEY-----"""


class PublicKeyCredentialsChecker:
    implements(checkers.ICredentialsChecker)
    #Only chek publick keys used by client
    credentialInterfaces = (credentials.ISSHPrivateKey,)

    #def __init__(self, dbpool):
    #  pass
      #self.dbpool = dbpool

    def requestAvatarId(self, credentials):
        # check http://wiki.velannes.com/doku.php?id=python:programmes:twisted_ssh_server
        publickey = base64.b64encode(credentials.blob)
        log.msg("My publickey:%s" % (publickey),logLevel=logging.DEBUG )
        log.msg("username %s" % (credentials.username),logLevel=logging.DEBUG)

	return defer.succeed(credentials.username)

        #return publickey
        # SQL Injection ...
        #defer = self.dbpool.runQuery("SELECT account FROM publickeys WHERE publickey = '%s'" % publickey)
        #defer.addCallback(self._cbRequestAvatarId, credentials)
        #defer.addErrback(self._ebRequestAvatarId)

        # return "sqale"
        #return defer

    # TODO
    def _cbRequestAvatarId(self, result, credentials):
        if result:
            return result[0][0]
        else:
            f = failure.Failure()
            log.err()
            return f

    # TODO
    def _ebRequestAvatarId(self, f):
        return f

class ProxySSHUser(avatar.ConchUser):

    def __init__(self, username):
        avatar.ConchUser.__init__(self)
        self.username = username
        self.otherGroups = []

        self.channelLookup.update({'session':session.SSHSession})
        self.subsystemLookup['sftp'] = filetransfer.FileTransferServer
	#here we can create the client
        log.msg("Start SFTPServerProxyClient")
        self.proxyclient = SFTPServerProxyClient()


    # Mac
    def getUserGroupId(self):
        return 1000,1000

    def getHomeDir(self):
        return '/home/rauburtin'

    def getOtherGroups(self):
        return self.otherGroups

    def _runAsUser(self, f, *args, **kw):
        euid = os.geteuid()
        egid = os.getegid()
        groups = os.getgroups()
        uid, gid = self.getUserGroupId()
        os.setegid(0)
        os.seteuid(0)
        os.setgroups(self.getOtherGroups())
        os.setegid(gid)
        os.seteuid(uid)
        try:
            f = iter(f)
        except TypeError:
            f = [(f, args, kw)]
        try:
            for i in f:
                func = i[0]
                args = len(i) > 1 and i[1] or ()
                kw = len(i) > 2 and i[2] or {}
                r = func(*args, **kw)
        finally:
            os.setegid(0)
            os.seteuid(0)
            os.setgroups(groups)
            os.setegid(egid)
            os.seteuid(euid)
        return r

    def logout(self):
        # Remove all listeners.
        log.msg("logout")
        for listener in self.listeners.itervalues():
            self._runAsUser(listener.stopListening)
        log.msg(
            'avatar %s logging out (%i)'
            % (self.username, len(self.listeners)))

class ProxySSHRealm:
    implements(portal.IRealm)

    def requestAvatar(self, avatarId, mind, *interfaces):
        return interfaces[0], ProxySSHUser(avatarId), lambda: None

class ProxySFTPSession(SFTPServerForUnixConchUser):

    def gotVersion(self, otherVersion, extData):
        if not hasattr(self.avatar.proxyclient, "client"):
            return {}
        else:
            log.msg("gitVersion otherVersion:% extData:%" % (otherVersion, extData), logLevel=logging.DEBUG)
            return self.avatar.proxyclient.client.gotVersion(otherVersion, extData)


    def openFile(self, filename, flags, attrs):
        log.msg("openFile filename:%s flags:%s attrs:%s" % (filename, flags, attrs), logLevel=logging.DEBUG)
        return self.avatar.proxyclient.client.openFile(filename, flags, attrs)


    def removeFile(self, filename):
        log.msg("removeFile filename:%s" % (filename), logLevel=logging.DEBUG)
        return self.avatar.proxyclient.client.removeFile(filename)


    def renameFile(self, oldpath, newpath):
        log.msg("renameFile oldpath:%s newpath:%s" % (oldpath, newpath), logLevel=logging.DEBUG)
        return self.avatar.proxyclient.client.renameFile(oldpath, newpath)


    def makeDirectory(self, path, attrs):
        log.msg("makeDirectory path:%s attrs:%s" % (path, attrs), logLevel=logging.DEBUG)
        return self.avatar.proxyclient.client.makeDirectory(path, attrs)

    def removeDirectory(self, path):
        log.msg("removeDirectory path:%s" % (path), logLevel=logging.DEBUG)
        return self.avatar.proxyclient.client.removeDirectory(path)


    def openDirectory(self, path):
        log.msg("openDirectory path:%s" % (path), logLevel=logging.DEBUG)
        files = []
        def _getFiles(openDir):
            def append(f):
                files.append(f)
                return openDir
            d = defer.maybeDeferred(openDir.next)
            d.addCallback(append)
            d.addCallback(_getFiles)
            d.addErrback(_close, openDir)
            return d

        def _close(_, openDir):
            d = openDir.close()
            return d
        def _setFiles(d,proxy):
            proxy.set_files(files)
            return d
        def _openDirectory(_,path):
           d = self.avatar.proxyclient.client.openDirectory(path)
           return d


        #not so bad, with _openDirectory(path)
        #d =  task.deferLater(reactor,1,_openDirectory,path)
        d = self.avatar.proxyclient.dcli
        d.addCallback(_openDirectory,path)
        d.addCallback(_getFiles)
        d.addCallback(ProxySFTPDirectory,files)

        return d

    def getAttrs(self, path, followLinks):
        log.msg("getAttrs path:%s followLinks:%s" % (path, followLinks), logLevel=logging.DEBUG)
        return self.avatar.proxyclient.client.getAttrs(path, followLinks)


    def setAttrs(self, path, attrs):
        log.msg("setAttrs path:%s attrs:%s" % (path, attrs), logLevel=logging.DEBUG)
        return self.avatar.proxyclient.client.setAttrs(path, attrs)


    def readLink(self, path):
        log.msg("readLink path:%s" % (path), logLevel=logging.DEBUG)
        return self.avatar.proxyclient.client.readLink(path)


    def makeLink(self, linkPath, targetPath):
        log.msg("makeLink linkPath:%s targetPath:%s" % (linkPath, targetPath), logLevel=logging.DEBUG)
        return self.avatar.proxyclient.client.makeLink(linkPath, targetPath)


    def realPath(self, path):
        if not hasattr(self.avatar.proxyclient, "client"):
            return os.path.realpath(self._absPath(path))
        else:
            log.msg("realPath path:%s" % (path), logLevel=logging.DEBUG)
            return self.avatar.proxyclient.client.realPath(path)


    def extendedRequest(self, extName, extData):
        raise NotImplementedError

class ProxySFTPDirectory:
    def __init__(self,d,files):
        self.files=files
    def set_files(self,files):
        self.files=files
    def __iter__(self):
        return self
    def next(self):
        try:
            f = self.files.pop(0)
            return (f[0],f[1],f[2])
        except IndexError:
            raise StopIteration
    def close(self):
        pass


class ProxySSHFactory(factory.SSHFactory):

    publicKeys  = { 'ssh-rsa': keys.Key.fromString(data=publicKey)   }
    privateKeys = { 'ssh-rsa': keys.Key.fromString(data=privateKey) }
    services = {
        'ssh-userauth': userauth.SSHUserAuthServer,
        'ssh-connection': connection.SSHConnection
    }

class ProxySFTPServer(object):
    def __init__(self, logfile=None):
        self.logfile = None
        if logfile:
            self.logfile = open(logfile, 'a')
            sys.stderr = self.logfile

        #dbpool = adbapi.ConnectionPool("MySQLdb", db='test', host='localhost', user='root')

    def run(self):

        global portal
        log.startLogging(sys.stdout)
        log.msg("Logging started")

        portal = portal.Portal(ProxySSHRealm())

        components.registerAdapter(ProxySFTPSession, ProxySSHUser, filetransfer.ISFTPServer)
        portal.registerChecker(PublicKeyCredentialsChecker())
        ProxySSHFactory.portal = portal

        reactor.listenTCP(5022, ProxySSHFactory())
        reactor.run()

if __name__ == '__main__':
    proxyserver = ProxySFTPServer()
    proxyserver.run()
