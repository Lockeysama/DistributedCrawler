# -*- coding: utf-8 -*-
'''
Created on 2017年4月12日

@author: chenyitao
'''

import gevent

from log import TDDCLogging
from conf import ParserSite
from common.queues import ParserQueues
from common import singleton
from . import StoragerBase


@singleton
class ParseStorager(StoragerBase):
    '''
    classdocs
    '''
    
    @staticmethod
    def push(task, items):
        ParserQueues.STORAGE.put((task, items))
        
    def _push(self):
        while True:
            task, items = ParserQueues.STORAGE.get()
            storage_items = {'valuable': items,
                             'task': {'task': task.to_json()}}
            if not self._db.put_to_hbase(task.platform + ParserSite.PLATFORM_SUFFIX, 
                                         task.row_key,
                                         storage_items):
                ParserQueues.STORAGE.put((task, items))
                gevent.sleep(1)

    def pull(self, task):
        ParserQueues.PARSE.put(task)

    def _pull(self):
        while True:
            task = ParserQueues.PARSE.get()
            if not task:
                continue
            if not task.platform or not task.row_key:
                TDDCLogging.error('Task Exception(Parse DB Manager): [%s:%s]' % (task.platform,
                                                                                 task.row_key))
                continue
            success, ret = self._db.get_from_hbase(task.platform + ParserSite.PLATFORM_SUFFIX,
                                                   task.row_key,
                                                   'source',
                                                   'content')
            if not success:
                ParserQueues.PARSE.put(task)
                gevent.sleep(1)
                continue
            if not ret:
                continue
            for _, value in ret.items():
                ParserQueues.WAITING_PARSE.put((task, value))
                break


def main():
    ParseStorager()
    while True:
        gevent.sleep()

if __name__ == '__main__':
    main()