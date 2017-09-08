# -*- coding: utf-8 -*-
'''
Created on 2017年5月8日

@author: chenyitao
'''

import json

import gevent
from tddc.common import TDDCLogging
from tddc.common.models import Task
from tddc.common.queues import PublicQueues

from ..plugins import DBManager


class StoragerBase(object):
    '''
    classdocs
    '''

    FAMILY = ''

    def __init__(self, nodes, push=True, pull=False):
        '''
        Constructor
        '''
        self._nodes = nodes
        TDDCLogging.info('-->Storager Manager Is Starting.')
        self._db = DBManager(self._nodes)
        if push:
            gevent.spawn(self._push)
            gevent.sleep()
        if pull:
            gevent.spawn(self._pull)
            gevent.sleep()
        TDDCLogging.info('-->Storager Manager Was Ready.')

    def push_onec(self, table, row_key, family, qualifier, content):
        storage_items = {'models': {family: {qualifier: content}}}
        if not self._db.put_to_hbase(table, 
                                     row_key,
                                     storage_items):
            return False
        return True

    @staticmethod
    def push(task, storage_info):
        PublicQueues.STORAGE.put((task, storage_info))

    def _push(self):
        cnt = 0
        platform_rows = {}
        while True:
            try:
                task, storage_info = PublicQueues.STORAGE.get()
                items = {self.FAMILY: storage_info,
                         'task': {'task': task.to_json()}}
                if not platform_rows.get(task.platform):
                    platform_rows[task.platform] = {}
                platform_rows[task.platform][task.row_key] = items
                cnt += 1
                if PublicQueues.STORAGE.qsize() and not cnt % 5:
                    gevent.sleep(0.01)
                    continue
                if self._db.puts_to_hbase(platform_rows):
                    self._pushed(platform_rows, True)
                else:
                    self._pushed(platform_rows, False)
                    gevent.sleep(1)
                platform_rows = {}
            except Exception, e:
                TDDCLogging.error(e)

    def _pushed(self, platform_rows, success):
        for _, rows in platform_rows.items():
            for _, row in rows.items():
                storage_info = row.get(self.FAMILY)
                task = Task(**json.loads(row.get('task').get('task')))
                if success:
                    self._push_success(task, storage_info)
                else:
                    PublicQueues.STORAGE.put((task, storage_info))
    
    def _push_success(self, task, storage_info):
        pass
    
    def pull_once(self, table, row_key, family=None, qualifier=None):
        success, ret = self._db.get_from_hbase(table,
                                               row_key,
                                               family,
                                               qualifier)
        if not success or not ret:
            return success, ret
        values = []
        for _, value in ret.items():
            values.append(value)
        return True, values
    
    def _pull(self):
        pass


def main():
    pass

if __name__ == '__main__':
    main()
