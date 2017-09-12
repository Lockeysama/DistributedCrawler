# -*- coding: utf-8 -*-
'''
Created on 2017年5月8日

@author: chenyitao
'''

import time

import gevent
from tddc.common.log.logger import TDDCLogging
from tddc.common.queues import PublicQueues

from ..plugins import RedisClient


class TaskStatusUpdater(RedisClient):
    '''
    classdocs
    '''

    def __init__(self, site):
        '''
        Constructor
        '''
        self.site = site
        super(TaskStatusUpdater, self).__init__(site.REDIS_NODES)
        gevent.spawn(self._create_record)
        gevent.sleep()
        self._successed_num = 0
        self._successed_pre_min = 0
        if site.STATUS_LOGGER_ENABLE: 
            gevent.spawn(self._status_printer)
            gevent.sleep()

    def _status_printer(self):
        while True:
            gevent.sleep(60)
            base = 'Successed Status: [All=%d] [Pre Minute:%d]'
            TDDCLogging.info(base % (self._successed_num,
                                     self._successed_pre_min))
            self._successed_pre_min = 0

    @staticmethod
    def create_record(task):
        PublicQueues.TASK_RECORD.put(task)

    def _create_record(self):
        while True:
            task = PublicQueues.TASK_RECORD.get()
            try:
                self.hset(self.site.RECORD_HSET_PREFIX + '.%s' % task.platform,
                          task.id,
                          task.to_json())
            except Exception, e:
                TDDCLogging.error(e)
                PublicQueues.TASK_RECORD.put(task)

    def update_status(self, task, new_status, old_status):
        if not new_status % 200:
            self._successed_pre_min += 1
            self._successed_num += 1
        self.hmove('%s.%s.%d' % (self.site.STATUS_HSET_PREFIX,
                                 task.platform,
                                 old_status),
                   '%s.%s.%d' % (self.site.STATUS_HSET_PREFIX,
                                 task.platform,
                                 new_status),
                   task.id,
                   str(int(time.time())))
