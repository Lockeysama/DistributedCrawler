# -*- coding: utf-8 -*-
'''
Created on 2017年4月17日

@author: chenyitao
'''
import gevent

from conf import ProxyCheckerSite
from conf.default import RedisSite
from common.queues import ProxyCheckerQueues
from common.models import IPInfo
from common import TDDCLogging
from ..base import IPPool


class ProxyManager(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        TDDCLogging.info('-->Proxy Manager Is Starting.')
        self._ip_pool = IPPool(RedisSite.REDIS_NODES)
        gevent.spawn(self._src_ip_fetch)
        gevent.sleep()
        gevent.spawn(self._useful_push)
        gevent.sleep()
        TDDCLogging.info('-->Proxy Manager Was Started.')
    
    def _useful_push(self):
        while True:
            info = ProxyCheckerQueues.USEFUL_PROXY.get()
            if self._ip_pool.sadd(ProxyCheckerSite.PLATFORM_PROXY_SET_KEY_BASE + info.platform,
                                  info.ip_port):
                self._ip_pool.publish(ProxyCheckerSite.PROXY_PUBSUB_PATTERN[:-1] + info.platform,
                                      info.ip_port)

    def _src_ip_fetch(self):
        while True:
            if ProxyCheckerQueues.HTTP_SOURCE_PROXY.qsize() < ProxyCheckerSite.CONCURRENT / 2:
                ret = self._ip_pool.smpop(ProxyCheckerSite.HTTP_SOURCE_PROXY_SET_KEY,
                                          ProxyCheckerSite.CONCURRENT * 2)
                ret = [item for item in ret if item]
                TDDCLogging.info('HTTP Add New: %d' % len(ret))
                for ip in ret:
                    ProxyCheckerQueues.HTTP_SOURCE_PROXY.put(IPInfo(ip_port=ip))
            if ProxyCheckerQueues.HTTPS_SOURCE_PROXY.qsize() < ProxyCheckerSite.CONCURRENT / 2:
                ret = self._ip_pool.smpop(ProxyCheckerSite.HTTPS_SOURCE_PROXY_SET_KEY,
                                          ProxyCheckerSite.CONCURRENT * 2)
                ret = [item for item in ret if item]
                TDDCLogging.info('HTTPS Add New: %d' % len(ret))
                for ip in ret:
                    ProxyCheckerQueues.HTTPS_SOURCE_PROXY.put(IPInfo(ip_port=ip, http_or_https='https'))
            gevent.sleep(5)


def main():
    ProxyManager()
    while True:
        info = ProxyCheckerQueues.HTTP_SOURCE_PROXY.get()
        print(info.ip_port, info.http_or_https)
#         info.platform = 'test'
#         USEFUL_PROXY_QUEUE.put(info)
        gevent.sleep(0.5)
        
    
if __name__ == '__main__':
    main()
