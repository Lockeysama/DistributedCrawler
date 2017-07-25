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
        TDDCLogging.info('--->Task Status Monitor Is Starting.')
        self._status = {}
        super(TaskStatusMonitor, self).__init__(MonitorSite.REDIS_NODES)
        gevent.spawn(self._get_status)
        gevent.sleep()
        TDDCLogging.info('--->Task Status Monitor Was Started.')

    def _get_status(self):
        while True:
            cur_time = time.time()  # 1495087998  # 
            keys = self.keys(MonitorSite.STATUS_HSET_PREFIX + '.*')
            for key in keys:
                platform, status = key.split('.')[-2:]
                h_len = self.hlen(key)
                if not self._status.get(platform):
                    self._status[platform] = {}
                self._status[platform][status] = h_len
                items = self.hscan_iter(key)
                self._task_timer_check(key, items, cur_time, status)
            self._print_status()
            gevent.sleep(60)
            self._status = {}

    def _task_timer_check(self, key, items, cur_time, status):
        if int(status) not in [Task.Status.WAIT_CRAWL,
                               Task.Status.WAIT_PARSE]:
            return
        del_list = []
        timeout_count = 0
        for _, (url, task) in enumerate(items):
            task = json.loads(task)
            task = Task(**task)
            timestamp = task.timestamp
            if int(timestamp) > cur_time - 60:
                continue
            MonitorQueues.NEW_EXCEPTION.put(task)
            TDDCLogging.debug(''.join(['[Platform: ', task.platform, '] ', 
                                       '[Status: ', str(task.status), '] ',
                                       '[Timeout: ', str(int(cur_time - timestamp)), 's]',
                                       '[URL: ', url, '] ']))
            del_list.append(url)
            if len(del_list) == 100:
                timeout_count += len(del_list)
                self.hmdel(key, del_list)
                del_list = []
        if len(del_list):
            timeout_count += len(del_list)
            self.hmdel(key, del_list)
        if timeout_count:
            TDDCLogging.info('Task Status(Timeout): [{}: {}].'.format(key, timeout_count))

    def _print_status(self):
        for platform, status in self._status.items():
            for state, count in status.items():
                if not count:
                    del status[state]
            if not len(status):
                del self._status[platform]
        status_info = json.dumps(self._status,
                                 sort_keys=True,
                                 indent=4) if len(self._status) else 'No Task Status.'
        TDDCLogging.debug(status_info)