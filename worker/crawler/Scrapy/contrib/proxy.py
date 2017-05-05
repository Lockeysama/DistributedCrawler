# -*- coding:utf-8 -*-
'''
Created on 2015年8月26日

@author: chenyitao
'''

import gevent

from common.queues import PLATFORM_PROXY_QUEUES
from worker.crawler.proxy_pool import IP_COOLING_POOL


class ProxyMiddleware(object):
    '''
    Proxy
    '''

    def process_request(self, request, spider):
        '''
        process request
        '''
        try:
            proxy = request.meta.get('proxy')
            if proxy:
                return
            task = request.meta.get('item')
            proxies = PLATFORM_PROXY_QUEUES.get(task.platform)
            while not proxies or not len(proxies):
                gevent.sleep(0.5)
                proxies = PLATFORM_PROXY_QUEUES.get(task.platform)
            ip_port = proxies.pop()
            proxies.add(ip_port)
            while IP_COOLING_POOL.in_pool(ip_port):
                proxies = PLATFORM_PROXY_QUEUES.get(task.platform)
                if len(proxies):
                    ip_port = proxies.pop()
                    proxies.add(ip_port)
                else:
                    gevent.sleep(0.5)
            IP_COOLING_POOL.push((ip_port, task.platform))
            ip, port = ip_port.split(':')
            proxy = '%s://%s:%s' % (task.proxy_type, ip, port)
            request.meta['proxy'] = proxy
            request.headers['X-Forwarded-For'] = ip_port
            request.headers['X-Real-IP'] = ip_port
        except Exception, e:
            print(e)


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
            proxies = PLATFORM_PROXY_QUEUES.get(task.platform)
            while not proxies or not len(proxies):
                gevent.sleep(0.5)
                proxies = PLATFORM_PROXY_QUEUES.get(task.platform)
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
