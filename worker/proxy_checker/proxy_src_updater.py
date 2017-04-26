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
import json


class ProxySourceUpdater(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self._ip_pool = IPPool()
        self._src_apis = [{'platform': 'kuaidaili',
                           'api':('http://dev.kuaidaili.com/api/getproxy/'
                                  '?orderid=999310215091675&num=100&'
                                  'b_pcchrome=1&b_pcie=1&b_pcff=1&'
                                  'protocol=1&method=1&an_an=1&'
                                  'an_ha=1&sp1=1&sp2=1&sp3=1&f_pr=1'
                                  '&dedup=1&format=json&sep=1'),
                           'parse_mould': self._parse_kuaidaili}]
        
    def start(self):
        while STATUS:
            for infos in self._src_apis:
                platform = infos.get('platform')
                api = infos.get('api')
                parse_mould = infos.get('parse_mould')
                rsp = requests.get(api)
                if not rsp:
                    print('Exception(%s): '%platform + api)
                    continue
                if not parse_mould:
                    print('Exception: parse_mould is None.')
                    continue
                all_ips = parse_mould(rsp.text)
                http_ips = self._proxy_active_check(all_ips.get('HTTP', []))
                self._ip_pool.msadd('tddc:test:proxy:ip_src:http', http_ips)
                print('Source IPS（HTTP） Growth：%d' % len(http_ips))
                https_ips = self._proxy_active_check(all_ips.get('HTTPS', []))
                self._ip_pool.msadd('tddc:test:proxy:ip_src:https', https_ips)
                print('Source IPS（HTTPS） Growth：%d' % len(https_ips))
            gevent.sleep(10)
    
    @staticmethod
    def _proxy_active_check(ips):
        active_ips = []
        
        def _checker(ip):
            try:
                _ip, _port = ip.split(':')
                _s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                _s.settimeout(5)
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
    
    def _parse_kuaidaili(self, data):
        proxies = {'HTTP': [], 'HTTPS': []}
        infos = json.loads(data)
        if infos.get('code'):
            return proxies
        proxy_list = infos.get('data').get('proxy_list', [])
        for proxy_info in proxy_list:
            proxy, proxy_type = proxy_info.split(',')
            proxies[proxy_type].append(proxy)
        return proxies

def main():
    import gevent.monkey
    gevent.monkey.patch_all()
    ProxySourceUpdater().start()
    
if __name__ == '__main__':
    main()

'''
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
'''