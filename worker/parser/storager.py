# -*- coding: utf-8 -*-
'''
Created on 2017年4月12日

@author: chenyitao
'''

import gevent

from conf.base_site import PLATFORM_SUFFIX
from common.queues import PARSE_QUEUE, WAITING_PARSE_QUEUE,\
    STORAGE_QUEUE
from common import TDDCLogging
from . import StoragerBase


class ParseDBManager(StoragerBase):
    '''
    classdocs
    '''
        
    def _push(self):
        while True:
            task, items = STORAGE_QUEUE.get()
            if not self._db.hbase_instance().put(task.platform + PLATFORM_SUFFIX,
                                                 task.row_key,
                                                 task,
                                                 items,
                                                 'valuable'):
                STORAGE_QUEUE.put((task, items))
                gevent.sleep(1)

    def _pull(self):
        while True:
            task = PARSE_QUEUE.get()
            if not task:
                continue
            if not task.platform or not task.row_key:
                TDDCLogging.error('Task Exception(Parse DB Manager): [%s:%s]' % (task.platform,
                                                                                 task.row_key))
                continue
            success, ret = self._db.get_from_hbase(task.platform + PLATFORM_SUFFIX,
                                                   task.row_key,
                                                   'source',
                                                   'content')
            if not success:
                PARSE_QUEUE.put(task)
                gevent.sleep(1)
                continue
            if not ret:
                continue
            for cv in ret.columnValues:
                if cv.qualifier == 'content':
                    WAITING_PARSE_QUEUE.put((task, cv.value))
                    break
            

def main():
    ParseDBManager()
    while True:
        gevent.sleep()

if __name__ == '__main__':
    main()