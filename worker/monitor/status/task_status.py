# -*- coding: utf-8 -*-
'''
Created on 2017年7月18日

@author: chenyitao
'''

import json
import time

import gevent

from base.plugins import RedisClient
from common import TDDCLogging
from common.models.task import Task
from common.queues.monitor import MonitorQueues
from conf import MonitorSite


class TaskStatusMonitor(RedisClient):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        TDDCLogging.info('-->Task Status Monitor Is Starting.')
        self._status = {}
        super(TaskStatusMonitor, self).__init__(MonitorSite.REDIS_NODES)
        gevent.spawn(self._get_status)
        gevent.sleep()
        TDDCLogging.info('-->Task Status Monitor Was Started.')

    def _get_status(self):
        while True:
            cur_time = 1495087998  # time.time()
            keys = self.keys(MonitorSite.STATUS_HSET_PREFIX + '.*')
            for key in keys:
                h_len = self.hlen(key)
                platform, status = key.split('.')[-2:]
                if not self._status.get(platform):
                    self._status[platform] = {}
                self._status[platform][status] = h_len
                items = self.hscan_iter(key)
                self._task_timer_check(items, cur_time)
            gevent.sleep(60)
            TDDCLogging.debug(json.dumps(self._status,
                                         sort_keys=True,
                                         indent=4))

    def _task_timer_check(self, items, cur_time):
        for index, (url, task) in enumerate(items):
            task = json.loads(task)
            task = Task(**task)
            time = task.timestamp
            if int(time) > cur_time - 20:
                continue
            MonitorQueues.EXCEPTION_TASK.put(task)
            TDDCLogging.debug(str(index) + ' : '
                              + task.platform + ' : ' 
                              + url + ' : '
                              + str(task.status) + ' : '
                              + str(time) + ' : '
                              + 'Crawl Again.')
            self.hdel(MonitorSite.STATUS_HSET_PREFIX, url)