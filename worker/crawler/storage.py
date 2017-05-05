# -*- coding: utf-8 -*-
'''
Created on 2017年4月14日

@author: chenyitao
'''

import gevent

from conf.base_site import STATUS, PLATFORM_SUFFIX
from common.queues import STORAGE_QUEUE, PARSE_QUEUE
from plugins.db.db_manager import DBManager


class CrawlStorager(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        print('-->Crawl Storager Is Starting.')
        gevent.spawn(self._push)
        gevent.sleep()
        print('-->Crawl Storager Was Ready.')
        
    def _push(self):
        _db = DBManager('Push')
        while STATUS:
            try:
                task, rsp_info = STORAGE_QUEUE.get()
                items = {'source': rsp_info,
                         'task': {'task': task.to_json()}}
                if _db.hbase_instance().put(task.platform + PLATFORM_SUFFIX, task.row_key, items):
                    PARSE_QUEUE.put(task)
                else:
                    STORAGE_QUEUE.put(task)
                    gevent.sleep(1)
            except Exception, e:
                print(e)


def main():
    CrawlStorager()
    while True:
        gevent.sleep()

if __name__ == '__main__':
    main()
