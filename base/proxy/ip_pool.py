# -*- coding: utf-8 -*-
'''
Created on 2017年4月19日

@author: chenyitao
'''

from conf.base_site import STATUS

from plugins.rsm.redis_manager.remote_shared_memory import RedisClient


class IPPool(object):
    
    def __init__(self, redis_client=None, callback=None):
        self._redis_client = redis_client
        self._callback = callback
        if not redis_client:
            self._redis_client = RedisClient()
        self._rdm = self._redis_client._rdm
        self._ready()
    
    def _ready(self):
        if self._callback:
            self._callback()
        
    def get(self, item):
        return self._rdm.get(item)
    
    def add(self, name, *values): 
        return self._rdm.sadd(name, *values)
        
    def msadd(self, name, values): 
        ppl = self._rdm.pipeline()
        for value in values:
            ppl.sadd(name, value)
        return ppl.execute()
    
    def randmember(self, name, count=1):
        return self._rdm.srandmember(name, count)
     
    def members(self, name):
        return self._rdm.smembers(name)
    
    def mspop(self, name, count):
        ppl = self._rdm.pipeline()
        for _ in xrange(count):
            ppl.spop(name)
        return ppl.execute()

    def remove(self, name, *values):
        self._rdm.srem(name, *values)

    def delete(self, *names):
        self._rdm.delete(*names)
        
    def scan(self, match):
        return self._rdm.scan_iter(match)

    def publish(self, channel, message):
        self._rdm.publish(channel, message)

    def psubscribe(self, pattern):
        ps = self._rdm.pubsub()
        ps.psubscribe(pattern)
        print('--->Pubsub Was Ready.')
        for item in ps.listen():
            yield item
            if not STATUS:
                ps.unsubscribe('spub')
                break
        print('-->Pubsub Is Exit.')


def main():
    import gevent.monkey
    gevent.monkey.patch_all()
    ip_pool = IPPool()
    
    rets = ip_pool.mspop('tddc:test:proxy:ip_src:http', 2)
    print(rets) 
    def subscribe(ip_pool):
        items = ip_pool.psubscribe('tddc:ip:platform:*')
        for item in items:
            print(item)
    
    gevent.spawn(subscribe, ip_pool)
    gevent.sleep()
    
    rdm = RedisClient()
    def publish(rdm, channel):
        for i in range(43):
            rdm._rdm.publish(channel, str(i))
            gevent.sleep(1)
    gevent.spawn(publish, rdm, 'tddc:ip:platform:cheok')
    gevent.sleep()
    gevent.spawn(publish, rdm, 'tddc:ip:platform:weidai')
    gevent.sleep()
    while True:
        gevent.sleep(60)

if __name__ == '__main__':
    main()
