# -*- coding: utf-8 -*-
'''
Created on 2017年4月19日

@author: chenyitao
'''

from plugins import RedisClient


class IPPool(RedisClient):
    pass


def main():
    from conf.base_site import REDIS_NODES
    import gevent.monkey
    gevent.monkey.patch_all()
    ip_pool = IPPool(REDIS_NODES)
    
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
