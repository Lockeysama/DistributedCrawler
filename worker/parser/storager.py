# -*- coding: utf-8 -*-
'''
Created on 2017年4月12日

@author: chenyitao
'''

import gevent

from conf.base_site import PLATFORM_SUFFIX, HBASE_HOST_PORTS
from common.queues import PARSE_QUEUE, WAITING_PARSE_QUEUE,\
    STORAGE_QUEUE
from plugins import DBManager
from common import TDDCLogging


class ParseDBManager(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        TDDCLogging.info('-->Parse DB Manager Is Starting.')
        gevent.spawn(self._push)
        gevent.sleep()
        gevent.spawn(self._fetch)
        gevent.sleep()
        TDDCLogging.info('-->Parse DB Manager Was Ready.')
        
    def _push(self):
        _db = DBManager('Push', HBASE_HOST_PORTS)
        while True:
            task, items = STORAGE_QUEUE.get()
            _db.hbase_instance().put(task.platform + PLATFORM_SUFFIX,
                                     task.row_key,
                                     task,
                                     items,
                                     'valuable')

    def _fetch(self):
        _db = DBManager('Fetch', HBASE_HOST_PORTS)
        while True:
            task = PARSE_QUEUE.get()
            if task:
                if not task.platform or not task.row_key:
                    print('Task Exception(Parse DB Manager):', task, task.platform, task.row_key)
                    continue
                ret = _db.hbase_instance().get(task.platform + PLATFORM_SUFFIX, task.row_key)
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