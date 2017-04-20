# -*- coding: utf-8 -*-
'''
Created on 2017年4月17日

@author: chenyitao
'''

import requests
from lxml import html

from conf.base_site import STATUS

class CheokProxyChecker(object):
    '''
    classdocs
    '''
    
    platform = 'cheok'
    
    proxy_type = 'http'
    
    check_page = 'http://www.cheok.com/'

    def __init__(self, info):
        '''
        Constructor
        '''
        self._info = info
        self.useful = False
        proxies = {'http': info.ip_port}
        headers = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) '
                                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                                  'Chrome/56.0.2924.87 Safari/537.36'),
                    'X-Forwarded-For': proxies['http'],
                    'X-Real-IP': proxies['http']}
        try:
            rsp = requests.get(self.check_page, proxies=proxies, timeout=5, headers=headers)
        except:
            pass
        else:
            if rsp.status_code != 200:
                return
            doc = html.document_fromstring(rsp.text)
            ret = doc.xpath('//*[@class="module-title"]')
            if len(ret):
                self.useful = True
        

def main():
    cnt = 0
    while STATUS:
        CheokProxyChecker('a')
        print(cnt)
        cnt += 1
    
    
if __name__ == '__main__':
    main()
