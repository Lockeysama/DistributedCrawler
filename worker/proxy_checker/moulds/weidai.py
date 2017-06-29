# -*- coding: utf-8 -*-
'''
Created on 2017年6月17日

@author: chenyitao
'''

import requests
from lxml import html


class WeidaiProxyChecker(object):
    '''
    classdocs
    '''
    
    platform = 'weidai'
    
    proxy_type = 'https'
    
    check_page = 'https://www.weidai.com.cn/list/showBidList'

    def __init__(self, info):
        '''
        Constructor
        '''
        self._info = info
        self.useful = False
        proxies = {'https': info.ip_port}
        headers = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) '
                                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                                  'Chrome/56.0.2924.87 Safari/537.36'),
                   'Referer': ('https://www.baidu.com/link'
                               '?url=pkWjNvxXASiNEqm3RznNOqP6kP8R8wzfqyT8thQEPkuTWX8wYU'
                               '-rgh9MmZPUAfc6dNnMHZPMXUxt_ZP0wtfSdK&wd=&eqid=d76a31670'
                               '024cbfa0000000459489cc6'),
                   'Cookie': ("_uab_collina=149127442516550634602802; "
                              "gr_user_id=8fe89878-0ccd-47e1-8d58-475c421db217; "
                              "aliyungf_tc=AQAAAIg8EybQLwEAvJF4fWxPE4WwTsah; "
                              "acw_tc=AQAAANljznQMsgEAvJF4fTcv0/yHtp4L; "
                              "route=fe730935a4f8fcc6ba142f2669a549fe; "
                              "JSESSIONID=AECA92FE7080D9D2ED7B7A9AEE273035; "
                              "gr_session_id_9e499063616a9fe6=4be824ae-41d6-4af8-bfed-5dc637616ce2; "
                              "14321=webim-visitor-Y6X8TBK4422XVVWV6RQM; "
                              "CNZZDATA1256511929=2103878879-1491272773-"
                              "https%253A%252F%252Fwww.baidu.com%252F%7C1497943668; ")}
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
                title = doc.xpath('//*/title/text()')
                if len(title) and title[0] == u'散标列表_我要投资_微贷网官网专业的投资平台':
                    self.useful = True
