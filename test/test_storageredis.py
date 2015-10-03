import os
import redis
from pysftpproxy.storageredis import StorageRedis
import unittest

class StorageRedisTest(unittest.TestCase):
    def setUp(self):
        redis_host = os.environ.get("SFTPPROXY_REDIS_HOST","localhost")
        redis_port = int(os.environ.get("SFTPPROXY_REDIS_PORT","6379"))
        redis_db = int(os.environ.get("SFTPPROXY_REDIS_DB","1"))
        redis_password = os.environ.get("SFTPPROXY_REDIS_PASSWORD",None)


        self.redis_conn = redis.Redis(redis_host,redis_port,
                redis_db,password=redis_password)

        self.pubkeys = {}
        self.pubkeys['AAAAB3NzaC1yc2EAAAABIwAAAGEArzJx8OYOnJmzf4tfBEvLi8DVPr' \
                'J3/c9k2I/Az64fxjHf9imyRJbixtQhlH9lfNjUIx+' \
                '4LmrJH5QNRsFporcHDKOTwTTYLh5KmRpslkYHRivcJSkbh/C+BR3utDS555mV'] = 'rauburtin'

        for pubkey,username in self.pubkeys.iteritems():
            self.redis_conn.set("pysftpproxy:pubkey:%s" % (pubkey),username)

        self.userinfos={}
        self.userinfos['rauburtin']={'remote':'localhost','port':'22'}

        for username,userinfo in self.userinfos.iteritems():
            self.redis_conn.hmset("pysftpproxy:user:%s" % (username),userinfo)

    def tearDown(self):
        for pubkey in self.pubkeys.keys():
            self.redis_conn.delete("pysftpproxy:pubkey:%s" % (pubkey))
        for username in self.userinfos.keys():
            self.redis_conn.delete("pysftpproxy:user:%s" % (username))

    def test_get1(self):
        sredis = StorageRedis()
        pubkey = 'AAAAB3NzaC1yc2EAAAABIwAAAGEArzJx8OYOnJmzf4tfBEvLi8DVPrJ3/c9k2I/Az64fxjHf9imyRJbixtQhlH9lfNjUIx+4LmrJH5QNRsFporcHDKOTwTTYLh5KmRpslkYHRivcJSkbh/C+BR3utDS555mV'
        username = sredis.get_username(pubkey)
        self.assertEqual(username,"rauburtin")

        userinfo = sredis.get_userinfo(username)
        self.assertDictEqual(userinfo,{'remote':'localhost','port':'22'})

    def test_add1(self):
        sredis = StorageRedis()
        pubkey = 'BAAAB3NzaC1yc2EAAAABIwAAAGEArzJx8OYOnJmzf4tfBEvLi8DVPrJ3/c9k2I/Az64fxjHf9imyRJbixtQhlH9lfNjUIx+4LmrJH5QNRsFporcHDKOTwTTYLh5KmRpslkYHRivcJSkbh/C+BR3utDS555mV'
        username = 'rauburtin1'
        self.assertTrue(sredis.add_username(pubkey,username))
        username = sredis.get_username(pubkey)
        self.assertEqual(username,"rauburtin1")

        self.assertTrue(sredis.add_userinfo(username,'localhost','22'))
        userinfo = sredis.get_userinfo(username)
        self.assertDictEqual(userinfo,{'remote':'localhost','port':'22'})

        sredis.del_username(pubkey)
        username = sredis.get_username(pubkey)
        self.assertIsNone(username)

        username="rauburtin1"
        sredis.del_userinfo(username)
        userinfo = sredis.get_userinfo(username)
        self.assertDictEqual(userinfo,{})




if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(StorageRedisTest) 
    unittest.TextTestRunner(verbosity=2).run(suite)
