# -*- coding: utf-8 -*-
'''
Created on 2017年4月17日

@author: chenyitao
'''

import requests
import socket
import gevent.pool
from plugins.rsm.redis_manager.ip_pool import IPPool

from conf.base_site import STATUS


class ProxySourceUpdater(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self._ip_pool = IPPool()
        self._src_apis = [{'platform': 'daili666',
                           'api': ('http://xvre.daili666api.com/ip/?'
                                   'tid=558465838696598'
                                   '&num=100'
                                   '&foreign=all'
                                   '&filter=off'
                                   '&protocol=http'
                                   '&delay=5'
                                   '&category=2'
                                   '&longlife=3'),
                           'parse_mould': self._parse_daili666,
                           'type': 'http'},
                          {'platform': 'daili666',
                           'api': ('http://xvre.daili666api.com/ip/?'
                                   'tid=558465838696598'
                                   '&num=100'
                                   '&foreign=all'
                                   '&filter=off'
                                   '&protocol=https'
                                   '&delay=5'
                                   '&category=2'
                                   '&longlife=3'),
                           'parse_mould': self._parse_daili666,
                           'type': 'https'}]
        
    def start(self):
        while STATUS:
            for infos in self._src_apis:
                platform = infos.get('platform')
                api = infos.get('api')
                parse_mould = infos.get('parse_mould')
                ips_type = infos.get('type')
                rsp = requests.get(api)
                if not rsp:
                    print('Exception(%s): '%platform + api)
                    continue
                if not parse_mould:
                    print('Exception: parse_mould is None.')
                    continue
                ips = self._proxy_active_check(parse_mould(rsp.text))
                self._ip_pool.msadd('tddc:test:proxy:ip_src:%s' % ips_type, ips)
                print('Source IPS（%s） Growth：%d' % (ips_type, len(ips)))
            gevent.sleep(10)
    
    def _proxy_active_check(self, ips):
        active_ips = []
        def _checker(ip):
            try:
                _ip, _port = ip.split(':')
                _s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                _s.settimeout(2)
                _s.connect((_ip, int(_port)))
                _s.close()
            except:
                pass
            else:
                active_ips.append(ip)
        
        p = gevent.pool.Pool(16)
        p.map(_checker, ips)
        p.join()
        return active_ips
    
    def _parse_daili666(self, data):
        return list(set(data.split('\r\n')))
        

def main():
    import gevent.monkey
    gevent.monkey.patch_all()
    ProxySourceUpdater().start()
    
if __name__ == '__main__':
    main()
