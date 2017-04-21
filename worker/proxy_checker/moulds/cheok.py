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
            try:
                doc = html.document_fromstring(rsp.text)
            except:
                pass
            else:
                ret = doc.xpath('//*[@class="module-title"]')
                if len(ret):
                    self.useful = True
        

def main():
    import csv
    import Queue
    import gevent
    import gevent.monkey
    gevent.monkey.patch_all()
    from worker.proxy_checker.models.IPInfo import IPInfo
    
    ips = Queue.Queue()
    csvfile = file('results.csv', 'rb')
    reader = csv.reader(csvfile)
    for line in reader:
        print(line)
        ips.put(IPInfo(line[0]+':8080'))
    
    def test():
        while True:
            ip = ips.get()
            ret = CheokProxyChecker(ip)
            if ret.useful:
                print(ip.ip_port)
#                 print(ret.useful)
    for _ in range(16):
        gevent.spawn(test)
        gevent.sleep()
        
    while STATUS:
        gevent.sleep(10)
    
    
if __name__ == '__main__':
    main()
