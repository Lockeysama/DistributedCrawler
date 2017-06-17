# -*- coding: utf-8 -*-
'''
Created on 2017年4月14日

@author: chenyitao
'''

import gevent

from common.queues import CrawlerQueues
from base import StoragerBase


class CrawlStorager(StoragerBase):
    '''
    classdocs
    '''
    
    FAMILY = 'source'

    def _push_success(self, task, storage_info):
        CrawlerQueues.PARSE.put((task, storage_info.get('rsp')[1] if storage_info.get('rsp') else None))


def main():
    CrawlStorager()
    while True:
        gevent.sleep()

if __name__ == '__main__':
    main()
