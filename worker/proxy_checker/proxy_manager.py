# -*- coding: utf-8 -*-
'''
Created on 2017年4月17日

@author: chenyitao
'''
import gevent

from conf.proxy_checker_site import PLATFORM_PROXY_SET_BASE_KEY,\
    HTTP_SOURCE_PROXY_SET_KEY, HTTPS_SOURCE_PROXY_SET_KEY, PROXY_PUBSUB_PATTERN, PROXY_CHECKER_CONCURRENT

from common.queues import HTTP_SOURCE_PROXY_QUEUE, HTTPS_SOURCE_PROXY_QUEUE,\
    USEFUL_PROXY_QUEUE

from worker.proxy_checker.models.IPInfo import IPInfo
from base.proxy.ip_pool import IPPool


class ProxyManager(object):
    '''
    classdocs
    '''

    def __init__(self, callback=None):
        '''
        Constructor
        '''
        self._callback = callback
        self._ip_pool = IPPool(callback=self._ip_pool_ready)
        gevent.spawn(self._src_ip_fetch)
        gevent.sleep()
        gevent.spawn(self._useful_push)
        gevent.sleep()
        self._ip_pool_ready()
        
    def _ip_pool_ready(self):
        if self._callback:
            self._callback()
            
    def _useful_push(self):
        while True:
            info = USEFUL_PROXY_QUEUE.get()
            if self._ip_pool.add(PLATFORM_PROXY_SET_BASE_KEY + info.platform, info.ip_port):
                self._ip_pool.publish(PROXY_PUBSUB_PATTERN[:-1] + info.platform, info.ip_port)

    def _src_ip_fetch(self):
        while True:
            if HTTP_SOURCE_PROXY_QUEUE.qsize() < PROXY_CHECKER_CONCURRENT / 2:
                ret = self._ip_pool.mspop(HTTP_SOURCE_PROXY_SET_KEY, PROXY_CHECKER_CONCURRENT * 2)
                ret = [item for item in ret if item]
                print('http+%d' % len(ret))
                for ip in ret:
                    HTTP_SOURCE_PROXY_QUEUE.put(IPInfo(ip))
            if HTTPS_SOURCE_PROXY_QUEUE.qsize() < PROXY_CHECKER_CONCURRENT / 2:
                ret = self._ip_pool.mspop(HTTPS_SOURCE_PROXY_SET_KEY, PROXY_CHECKER_CONCURRENT * 2)
                ret = [item for item in ret if item]
                print('https+%d' % len(ret))
                for ip in ret:
                    HTTPS_SOURCE_PROXY_QUEUE.put(IPInfo(ip, 'https'))
            gevent.sleep(5)


def main():
    ProxyManager()
    while True:
        info = HTTP_SOURCE_PROXY_QUEUE.get()
        print(info.ip_port, info.http_or_https)
#         info.platform = 'test'
#         USEFUL_PROXY_QUEUE.put(info)
        gevent.sleep(0.5)
        
    
if __name__ == '__main__':
    main()
