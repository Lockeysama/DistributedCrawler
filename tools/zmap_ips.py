# -*- coding: utf-8 -*-
'''
Created on 2017年4月25日

@author: chenyitao
'''

import csv

from base.proxy.ip_pool import IPPool
import time

def main():
    ips = []
    csvfile = file('results.csv', 'rb')
    reader = csv.reader(csvfile)
    for line in reader:
        ips.append('%s:808' % line)
    ip_pool = IPPool()
    ip_pool.msadd('tddc:test:proxy:ip_src:%s' % 'http', ips)
    

if __name__ == '__main__':
    main()
    while True:
        time.sleep(10)
