# -*- coding: utf-8 -*-
'''
Created on 2017年4月14日

@author: chenyitao
'''

import gevent
import random

from conf.base_site import REDIS_NODES
from conf.proxy_checker_site import PROXY_PUBSUB_PATTERN, PLATFORM_PROXY_SET_BASE_KEY
from common.queues import PLATFORM_PROXY_QUEUES, UNUSEFUL_PROXY_FEEDBACK_QUEUE

from common import TDDCLogging
from . import IPPool
from worker.base.proxy.ip_cooling_pool import IPCoolingPoll


class CrawlProxyPool(object):
    '''
    classdocs
    '''
    
    IP_COOLING_POOL = IPCoolingPoll()

    def __init__(self):
        '''
        Constructor
        '''
        TDDCLogging.info('-->Crawl Proxy Pool Is Starting.')
        self._ip_pool = IPPool(REDIS_NODES)
        self._init_proxy()
        gevent.spawn(self._subscribe)
        gevent.sleep()
        gevent.spawn(self._proxy_unuseful_feedback)
        gevent.sleep()
        TDDCLogging.info('-->Crawl Proxy Pool Was Ready.')
    
    @staticmethod
    def get_proxy(platform):
        for _ in range(3):
            if not PLATFORM_PROXY_QUEUES.get(platform):
                gevent.sleep(1)
            else:
                break
        else:
            return CrawlProxyPool.get_random_proxy()
        while not len(PLATFORM_PROXY_QUEUES.get(platform)):
            gevent.sleep(1)
        proxies = PLATFORM_PROXY_QUEUES.get(platform)
        proxy = proxies.pop()
        while CrawlProxyPool.IP_COOLING_POOL.in_pool((proxy, platform)):
            proxy = proxies.pop()
        CrawlProxyPool.IP_COOLING_POOL.push((proxy, platform))
        return proxy
        
    @staticmethod
    def get_random_proxy():
        for _, proxies in PLATFORM_PROXY_QUEUES.items():
            return random.choice(list(proxies))
    
    def _init_proxy(self):
        s = self._ip_pool.scan_iter(PLATFORM_PROXY_SET_BASE_KEY + '*')
        for ret in s:
            key = ret.encode('utf-8')
            platform = key.split(':')[-1]
            ips = self._ip_pool.smembers(key)
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
    
    def _proxy_unuseful_feedback(self):
        while True:
            platform, proxy = UNUSEFUL_PROXY_FEEDBACK_QUEUE.get()
            if proxy in PLATFORM_PROXY_QUEUES.get(platform, set()): 
                PLATFORM_PROXY_QUEUES[platform].remove(proxy)
                self._ip_pool.srem(PLATFORM_PROXY_SET_BASE_KEY + platform,
                                   proxy.encode('utf-8'))


def main():
    import gevent.monkey
    gevent.monkey.patch_all()
    cpm = CrawlProxyPool()

    def test():
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