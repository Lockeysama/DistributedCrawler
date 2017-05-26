# -*- coding: utf-8 -*-
'''
Created on 2017年4月14日

@author: chenyitao
'''

import gevent
import random

from conf import CrawlerSite
from common.queues import CrawlerQueues

from log import TDDCLogging
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
        self._ip_pool = IPPool(CrawlerSite.REDIS_NODES)
        self._init_proxy()
        gevent.spawn(self._subscribe)
        gevent.sleep()
        gevent.spawn(self._proxy_unuseful_feedback)
        gevent.sleep()
        TDDCLogging.info('-->Crawl Proxy Pool Was Ready.')

    @staticmethod
    def get_proxy(platform):
        for _ in range(3):
            if not CrawlerQueues.PLATFORM_PROXY.get(platform):
                gevent.sleep(1)
            else:
                break
        else:
            return CrawlProxyPool.get_random_proxy()
        while not len(CrawlerQueues.PLATFORM_PROXY.get(platform)):
            gevent.sleep(1)
        proxies = CrawlerQueues.PLATFORM_PROXY.get(platform)
        proxy = proxies.pop()
        while CrawlProxyPool.IP_COOLING_POOL.in_pool((proxy, platform)):
            proxy = proxies.pop()
        CrawlProxyPool.IP_COOLING_POOL.push((proxy, platform))
        return proxy
        
    @staticmethod
    def get_random_proxy():
        for _, proxies in CrawlerQueues.PLATFORM_PROXY.items():
            return random.choice(list(proxies))
    
    def _init_proxy(self):
        s = self._ip_pool.scan_iter(CrawlerSite.PLATFORM_PROXY_SET_KEY_BASE + '*')
        for ret in s:
            key = ret.encode('utf-8')
            platform = key.split(':')[-1]
            ips = self._ip_pool.smembers(key)
            if not CrawlerQueues.PLATFORM_PROXY.get(platform):
                CrawlerQueues.PLATFORM_PROXY[platform] = set()
            CrawlerQueues.PLATFORM_PROXY[platform] |= set(ips)
    
    def _subscribe(self):
        items = self._ip_pool.psubscribe(CrawlerSite.PROXY_PUBSUB_PATTERN)
        for item in items:
            if item.get('type') == 'psubscribe':
                TDDCLogging.info('---->Subscribe: %s' % item.get('channel'))
                continue
            platform = item.get('channel', '').split(':')[-1]
            data = item.get('data')
            if not CrawlerQueues.PLATFORM_PROXY.get(platform):
                CrawlerQueues.PLATFORM_PROXY[platform] = set()
            CrawlerQueues.PLATFORM_PROXY[platform].add(data)
    
    def _proxy_unuseful_feedback(self):
        while True:
            platform, proxy = CrawlerQueues.UNUSEFUL_PROXY_FEEDBACK.get()
            if proxy in CrawlerQueues.PLATFORM_PROXY.get(platform, set()): 
                CrawlerQueues.PLATFORM_PROXY[platform].remove(proxy)
                self._ip_pool.srem(CrawlerSite.PLATFORM_PROXY_SET_KEY_BASE + platform,
                                   proxy.encode('utf-8'))


def main():
    import gevent.monkey
    gevent.monkey.patch_all()
    cpm = CrawlProxyPool()

    def test():
        while True:
            if CrawlerQueues.PLATFORM_PROXY.get('cheok'):
                ip = random.choice(list(CrawlerQueues.PLATFORM_PROXY['cheok']))
                CrawlerQueues.UNUSEFUL_PROXY_FEEDBACK.put(['cheok', ip])
            gevent.sleep(1)
    
    gevent.spawn(test)
    gevent.sleep()
    
    def publish(ip_pool, channel, publish_channel):
        for i in range(43):
            ip = '192.168.1.' + str(i)
            ip_pool.add(channel, ip)
            ip_pool._rdm.publish(publish_channel, ip)
            gevent.sleep(1)
    gevent.spawn(publish,
                 cpm._ip_pool,
                 CrawlerSite.PLATFORM_PROXY_SET_KEY_BASE + 'cheok',
                 CrawlerSite.PROXY_PUBSUB_PATTERN[:-1] + 'cheok')
    gevent.sleep()
    while True:
        gevent.sleep(60)

if __name__ == '__main__':
    main()