# -*- coding: utf-8 -*-
'''
Created on 2017年4月14日

@author: chenyitao
'''

import gevent

from conf.base_site import STATUS
from common.queues import PLATFORM_PROXY_QUEUES, UNUSEFUL_PROXY_FEEDBACK_QUEUE

from plugins.rsm.redis_manager.ip_pool import IPPool
from conf.proxy_checker_site import PROXY_PUBSUB_PATTERN,\
    PLATFORM_PROXY_SET_BASE_KEY
import threading

class CrawlerProxyManager(object):
    '''
    classdocs
    '''

    def __init__(self, callback=None):
        '''
        Constructor
        '''
        self._callback = callback
        self._ip_pool = IPPool()
        self._init_proxy()
        gevent.spawn(self._subscribe)
        gevent.sleep()
        gevent.spawn(self._proxy_unuseful_feedback, self._ip_pool)
        gevent.sleep()
        
    def _ready(self):
        if self._callback:
            self._callback(self)
    
    def _init_proxy(self):
        s = self._ip_pool.scan(PLATFORM_PROXY_SET_BASE_KEY + '*')
        for ret in s:
            key = ret.encode('utf-8')
            platform = key.split(':')[-1]
            ips = self._ip_pool.members(key)
            if not PLATFORM_PROXY_QUEUES.get(platform):
                PLATFORM_PROXY_QUEUES[platform] = set()
            PLATFORM_PROXY_QUEUES[platform] |= set(ips)
    
    def _subscribe(self):
        items = self._ip_pool.psubscribe(PROXY_PUBSUB_PATTERN)
        self._ready()
        for item in items:
            if item.get('type') == 'psubscribe':
                print('---->Subscribe: %s' % item.get('channel'))
                continue
            platform = item.get('channel', '').split(':')[-1]
            data = item.get('data')
            if not PLATFORM_PROXY_QUEUES.get(platform):
                PLATFORM_PROXY_QUEUES[platform] = set()
            PLATFORM_PROXY_QUEUES[platform].add(data)
    
    def _proxy_unuseful_feedback(self, ip_pool):
        lock = threading.Lock()
        while STATUS:
            if lock.acquire():
                try:
                    platform, proxy = UNUSEFUL_PROXY_FEEDBACK_QUEUE.get()
                    PLATFORM_PROXY_QUEUES[platform].remove(proxy)
                    ip_pool.remove(PLATFORM_PROXY_SET_BASE_KEY+platform, proxy.encode('utf-8'))
                except Exception, e:
                    print('========>',e)
                finally:
                    lock.release()
        
        
def main():
    import gevent.monkey
    gevent.monkey.patch_all()
    cpm = CrawlerProxyManager()

    def test():
        import random
        while STATUS:
            if PLATFORM_PROXY_QUEUES.get('cheok'):
                ip = random.choice(list(PLATFORM_PROXY_QUEUES['cheok']))
                UNUSEFUL_PROXY_FEEDBACK_QUEUE.put(['cheok', ip])
            gevent.sleep(1)
    
    gevent.spawn(test)
    gevent.sleep()
    
    def publish(ip_pool, channel, publish_channel):
        for i in range(43):
            ip = '192.168.1.' + str(i)
            ip_pool.add(channel, ip)
            ip_pool._rdm.publish(publish_channel, ip)
            gevent.sleep(1)
    gevent.spawn(publish, cpm._ip_pool, PLATFORM_PROXY_SET_BASE_KEY + 'cheok', PROXY_PUBSUB_PATTERN[:-1] + 'cheok')
    gevent.sleep()
    while True:
        gevent.sleep(60)

if __name__ == '__main__':
    main()