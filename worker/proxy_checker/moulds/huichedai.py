# -*- coding: utf-8 -*-
'''
Created on 2017年6月29日

@author: chenyitao
'''

import requests
from lxml import html


class Huichedai(object):
    '''
    classdocs
    '''
    
    platform = 'huichedai'
    
    proxy_type = 'http'
    
    check_page = 'http://www.huichedai.com/invest/index.html'

    def __init__(self, info):
        '''
        Constructor
        '''
        self._info = info
        self.useful = False
        proxies = {'http': info.ip_port}
        headers = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) '
                                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                                  'Chrome/56.0.2924.87 Safari/537.36')}
        try:
            rsp = requests.get(self.check_page, proxies=proxies, timeout=5, headers=headers)
        except:
            pass
        else:
            if rsp.status_code != 200:
                return
            try:
                doc = html.document_fromstring(rsp.text)
            except:
                pass
            else:
                ret = doc.xpath('//*[@class="invest-item simple-item mgt "]')
                if len(ret):
                    self.useful = True
