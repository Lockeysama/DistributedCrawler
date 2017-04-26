# -*- coding:utf-8 -*-
'''
Created on 2015年8月26日

@author: chenyitao
'''

from common.queues import PLATFORM_PROXY_QUEUES
import random
import gevent

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
            ip_port = random.choice(list(proxies))
            ip, port = ip_port.split(':')
            proxy = '%s://%s:%s' % (task.proxy_type, ip, port)
            request.meta['proxy'] = proxy
            request.headers['X-Forwarded-For'] = ip_port
            request.headers['X-Real-IP'] = ip_port
        except Exception, e:
            print(e)
