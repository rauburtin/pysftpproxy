#!/usr/bin/env python
from pysftpproxy.storageredis import  StorageRedis
sredis = StorageRedis()

pubkey=open("/home/rauburtin/.ssh/id_rsa.pub","r").read()
if pubkey.endswith("\n"):
    pubkey = pubkey[:-1]
if len(pubkey.split())==3:
    pubkey = ' '.join(pubkey.split()[:-1])
if len(pubkey.split())==2:
    pubkey = pubkey.split()[1]
username="rauburtin"

sredis.add_username(pubkey,username)
sredis.add_userinfo(username,"192.168.22.14","32772","root")

