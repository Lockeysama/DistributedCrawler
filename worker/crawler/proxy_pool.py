# -*- coding: utf-8 -*-
'''
Created on 2017年4月14日

@author: chenyitao
'''

import gevent

from conf.proxy_checker_site import PROXY_PUBSUB_PATTERN, PLATFORM_PROXY_SET_BASE_KEY
from common import TDDCLogging
from common.queues import PLATFORM_PROXY_QUEUES, UNUSEFUL_PROXY_FEEDBACK_QUEUE

from . import IPPool
from .Scrapy.contrib.ip_cooling_pool import IPCoolingPoll
IP_COOLING_POOL = IPCoolingPoll()


class CrawlProxyPool(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        TDDCLogging.info('-->Crawl Proxy Pool Is Starting.')
        self._ip_pool = IPPool()
        self._init_proxy()
        gevent.spawn(self._subscribe)
        gevent.sleep()
        gevent.spawn(self._proxy_unuseful_feedback, self._ip_pool)
        gevent.sleep()
        TDDCLogging.info('-->Crawl Proxy Pool Was Ready.')
    
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
        for item in items:
            if item.get('type') == 'psubscribe':
                TDDCLogging.info('---->Subscribe: %s' % item.get('channel'))
                continue
            platform = item.get('channel', '').split(':')[-1]
            data = item.get('data')
            if not PLATFORM_PROXY_QUEUES.get(platform):
                PLATFORM_PROXY_QUEUES[platform] = set()
            PLATFORM_PROXY_QUEUES[platform].add(data)
    
    def _proxy_unuseful_feedback(self, ip_pool):
        while True:
            platform, proxy = UNUSEFUL_PROXY_FEEDBACK_QUEUE.get()
            if proxy in PLATFORM_PROXY_QUEUES.get(platform, set()): 
                PLATFORM_PROXY_QUEUES[platform].remove(proxy)
                ip_pool.remove(PLATFORM_PROXY_SET_BASE_KEY+platform, proxy.encode('utf-8'))


def main():
    import gevent.monkey
    gevent.monkey.patch_all()
    cpm = CrawlProxyPool()

    def test():
        import random
        while True:
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