# -*- coding: utf-8 -*-
'''
Created on 2017年4月14日

@author: chenyitao
'''

import gevent

from conf.base_site import STATUS, PLATFORM_SUFFIX
from conf.crawler_site import DB_PUSH_CONCURRENT
from common.queues import STORAGE_QUEUE, PARSE_QUEUE
from plugins.db.db_manager import DBManager
from worker.parser.models.parse_task import ParseTask


class CrawlDBManager(object):
    '''
    classdocs
    '''

    def __init__(self, callback=None):
        '''
        Constructor
        '''
        print('-->Crawl DB Manager Is Starting.')
        self._callback = callback
        for i in range(DB_PUSH_CONCURRENT):
            gevent.spawn(self._push, i)
            gevent.sleep()
        self._parse_db_manager_was_ready()
        
    def _parse_db_manager_was_ready(self):
        print('-->Crawl DB Manager Was Ready.')
        if self._callback:
            self._callback(self)

    def _push(self, tag):
        _db = DBManager('Push[%d]' % tag)
        while STATUS:
            task, items = STORAGE_QUEUE.get()
            _db.hbase_instance().put(task.platform + PLATFORM_SUFFIX, task.row_key, task, items, 'source')
            parse_task = ParseTask(task, items)
            PARSE_QUEUE.put(parse_task)


def main():
    CrawlDBManager()
    while True:
        gevent.sleep()

if __name__ == '__main__':
    main()
