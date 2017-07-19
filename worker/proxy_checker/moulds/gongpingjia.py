# -*- coding: utf-8 -*-
'''
Created on 2017年7月14日

@author: chenyitao
'''

import requests
from lxml import html


class GongpingjiaProxyChecker(object):
    '''
    classdocs
    '''
    
    platform = 'gongpingjia'
    
    proxy_type = 'http'
    
    check_page = 'http://hz.gongpingjia.com/'
    
    headers = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) '
                              'AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/56.0.2924.87 Safari/537.36'),
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
               'Accept-Encoding': 'gzip, deflate, sdch',
               'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
               'Cache-Control': 'max-age=0',
               'Connection': 'keep-alive',
               'DNT': '1',
               'Host': 'hz.gongpingjia.com',
               'Upgrade-Insecure-Requests': '1'}

    def __init__(self, info):
        '''
        Constructor
        '''
        self._info = info
        self.useful = False
        self._request()

    def _request(self, times=0):
        if times > 3:
            return
        proxies = {'http': self._info.ip_port}
        try:
            rsp = requests.get(self.check_page, proxies=proxies, timeout=10, headers=self.headers)
        except:
            pass
        else:
            if rsp.status_code != 200:
                if rsp.status_code >= 500:
                    self._request(times + 1)
                return
            try:
                doc = html.document_fromstring(rsp.text)
            except:
                pass
            else:
                ret = doc.xpath('//head/title/text()')
                if len(ret):
                    self.useful = True
