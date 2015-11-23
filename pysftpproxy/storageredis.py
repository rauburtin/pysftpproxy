import redis
import os
import unittest
class StorageRedis(object):
    def __init__(self):
        redis_host = os.environ.get("SFTPPROXY_REDIS_HOST","localhost")
        redis_port = int(os.environ.get("SFTPPROXY_REDIS_PORT","6379"))
        redis_db = int(os.environ.get("SFTPPROXY_REDIS_DB","1"))
        redis_password = os.environ.get("SFTPPROXY_REDIS_PASSWORD",None)


        self.redis_conn = redis.Redis(redis_host,redis_port,
                redis_db,password=redis_password)

    def get_username(self,pubkey):
        return self.redis_conn.get("pysftpproxy:pubkey:%s" % (pubkey))

    def get_userinfo(self,username):
        return self.redis_conn.hgetall("pysftpproxy:user:%s" % (username))

    def add_username(self,pubkey,username):
        return self.redis_conn.set("pysftpproxy:pubkey:%s" % (pubkey), username) 

    def add_userinfo(self,username,remote,port,user):
        return self.redis_conn.hmset("pysftpproxy:user:%s" % (username),
                {'remote':remote,'port':port,'user':user})

    def del_username(self,pubkey):
        return self.redis_conn.delete("pysftpproxy:pubkey:%s" % (pubkey))

    def del_userinfo(self,username):
        return self.redis_conn.delete("pysftpproxy:user:%s" % (username))


