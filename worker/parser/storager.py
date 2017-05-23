# -*- coding: utf-8 -*-
'''
Created on 2017年4月12日

@author: chenyitao
'''

import gevent

from conf.base_site import PLATFORM_SUFFIX
from common.queues_define import PARSE_QUEUE, WAITING_PARSE_QUEUE,\
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
            storage_items = {'valuable': items,
                             'task': {'task': task.to_json()}}
            if not self._db.put_to_hbase(task.platform + PLATFORM_SUFFIX, 
                                         task.row_key,
                                         storage_items):
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
            for _, value in ret.items():
                WAITING_PARSE_QUEUE.put((task, value))
                break
            

def main():
    ParseDBManager()
    while True:
        gevent.sleep()

if __name__ == '__main__':
    main()