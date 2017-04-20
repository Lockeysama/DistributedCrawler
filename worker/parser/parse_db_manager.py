# -*- coding: utf-8 -*-
'''
Created on 2017年4月12日

@author: chenyitao
'''

import gevent

from conf.base_site import STATUS
from conf.parser_site import DB_FETCH_CONCURRENT, DB_PUSH_CONCURRENT
from common.queues import PARSE_QUEUE, WAITING_PARSE_QUEUE,\
    STORAGE_QUEUE
from plugins.db.db_manager import DBManager
from worker.parser.models.parse_task import ParseTask

SIGNAL_DB_READY = object()

class ParseDBManager(object):
    '''
    classdocs
    '''

    def __init__(self, callback=None):
        '''
        Constructor
        '''
        print('-->Parse DB Manager Is Starting.')
        self._callback = callback
        for i in range(DB_PUSH_CONCURRENT):
            gevent.spawn(self._push, i)
            gevent.sleep()
        for i in range(DB_FETCH_CONCURRENT):
            gevent.spawn(self._fetch, i)
            gevent.sleep()
        self._parse_db_manager_was_ready()
        
    def _parse_db_manager_was_ready(self):
        print('-->Parse DB Manager Was Ready.')
        if self._callback:
            self._callback(self, SIGNAL_DB_READY, None)

    def _push(self, tag):
        _db = DBManager('Push[%d]' % tag)
        while STATUS:
            task, items = STORAGE_QUEUE.get()
            _db.hbase_instance().put(task.platform, task.row_key, task, items, 'valuable')

    def _fetch(self, tag):
        _db = DBManager('Fetch[%d]' % tag)
        while STATUS:
            task = PARSE_QUEUE.get()
            if task:
                if not task.platform or not task.row_key:
                    print('Task Exception(Parse DB Manager):', task, task.platform, task.row_key)
                    continue
                ret = _db.hbase_instance().get(task.platform, task.row_key)
                if not ret:
                    continue
                for cv in ret.columnValues:
                    if cv.qualifier == 'content':
                        parse_task = ParseTask(task, {'body': cv.value})
                        WAITING_PARSE_QUEUE.put(parse_task)
                        break
            

def main():
    ParseDBManager()
    while True:
        gevent.sleep()

if __name__ == '__main__':
    main()