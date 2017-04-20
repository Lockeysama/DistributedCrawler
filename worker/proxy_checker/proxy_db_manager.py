# -*- coding: utf-8 -*-
'''
Created on 2017年4月17日

@author: chenyitao
'''
import gevent

from conf.base_site import STATUS
from conf.proxy_checker_site import PLATFORM_PROXY_SET_BASE_KEY,\
    HTTP_SOURCE_PROXY_SET_KEY, HTTPS_SOURCE_PROXY_SET_KEY, PROXY_PUBSUB_PATTERN

from common.queues import HTTP_SOURCE_PROXY_QUEUE, HTTPS_SOURCE_PROXY_QUEUE,\
    USEFUL_PROXY_QUEUE

from worker.proxy_checker.models.IPInfo import IPInfo
from plugins.rsm.redis_manager.ip_pool import IPPool


class ProxyDBManager(object):
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
        
    def _ip_pool_ready(self):
        if self._callback:
            self._callback()
            
    def _useful_push(self):
        while STATUS:
            info = USEFUL_PROXY_QUEUE.get()
            self._ip_pool.add(PLATFORM_PROXY_SET_BASE_KEY + info.platform,
                              info.ip_port)
            self._ip_pool.publish(PROXY_PUBSUB_PATTERN[:-1] + info.platform, info.ip_port)

    def _src_ip_fetch(self):
        while STATUS:
            if HTTP_SOURCE_PROXY_QUEUE.empty():
                ret = self._ip_pool.members(HTTP_SOURCE_PROXY_SET_KEY)
                for ip in ret:
                    info = IPInfo()
                    info.ip_port = ip
                    HTTP_SOURCE_PROXY_QUEUE.put(info)
            elif HTTPS_SOURCE_PROXY_QUEUE.empty():
                ret = self._ip_pool.members(HTTPS_SOURCE_PROXY_SET_KEY)
                for ip in ret:
                    info = IPInfo()
                    info.ip_port = ip
                    HTTPS_SOURCE_PROXY_QUEUE.put(info)
            else:
                gevent.sleep(10)


def main():
    ProxyDBManager()
    while STATUS:
        info = HTTP_SOURCE_PROXY_QUEUE.get()
        info.platform = 'test'
        USEFUL_PROXY_QUEUE.put(info)
        gevent.sleep(0.5)
        
    
if __name__ == '__main__':
    main()
