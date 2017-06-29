# -*- coding:utf-8 -*-
'''
Created on 2015年8月26日

@author: chenyitao
'''

import gevent

from common.queues import CrawlerQueues
from worker.crawler.proxy_pool import CrawlProxyPool


class ProxyMiddleware(object):
    '''
    Proxy
    '''

    def process_request(self, request, spider):
        '''
        process request
        '''
        proxy = request.meta.get('proxy')
        if not proxy:
            task, _ = request.meta.get('item')
            if task.proxy_type != 'None':
                ip_port = CrawlProxyPool.get_proxy(task.platform)
                ip, port = ip_port.split(':')
                proxy = '%s://%s:%s' % (task.proxy_type if task.proxy_type else 'http', ip, port)
                request.meta['proxy'] = proxy
#                 request.headers['X-Forwarded-For'] = '10.10.10.10'
#                 request.headers['X-Real-IP'] = '10.10.10.10'


CURRENT_PROXY = None

class ProxyMiddlewareExtreme(object):
    '''
    Proxy
    '''

    def process_request(self, request, spider):
        '''
        process request
        '''
        global CURRENT_PROXY
        task = request.meta.get('item')
        if CURRENT_PROXY:
            self.set_proxy(task, request)
            return
        try:
            proxies = CrawlerQueues.PLATFORM_PROXY.get(task.platform)
            while not proxies or not len(proxies):
                gevent.sleep(0.5)
                proxies = CrawlerQueues.PLATFORM_PROXY.get(task.platform)
            ip_port = proxies.pop()
            CURRENT_PROXY = ip_port
            self.set_proxy(task, request)
        except Exception, e:
            print(e)

    def set_proxy(self, task, request):
        global CURRENT_PROXY
        proxy = '%s://%s' % (task.proxy_type, CURRENT_PROXY)
        request.meta['proxy'] = proxy
        request.headers['X-Forwarded-For'] = CURRENT_PROXY
        request.headers['X-Real-IP'] = CURRENT_PROXY
