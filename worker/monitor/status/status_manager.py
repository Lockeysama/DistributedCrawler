# -*- coding: utf-8 -*-
'''
Created on 2017年5月17日

@author: chenyitao
'''

import json
import time

import gevent

from base.plugins import RedisClient
from common import TDDCLogging
from common.models.task import Task
from common.queues.monitor import MonitorQueues
from conf.monitor_site import MonitorSite


class StatusManager(RedisClient):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        TDDCLogging.info('-->Status Manager Is Starting.')
        self._status = {}
        super(StatusManager, self).__init__(MonitorSite.REDIS_NODES)
        gevent.spawn(self._get_status)
        gevent.sleep()
        TDDCLogging.info('-->Status Manager Was Started.')
    
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
                item = self.hscan_iter(key)
                for index, (url, task) in enumerate(item):
                    task = json.loads(task)
                    task = Task(**task)
                    time = task.timestamp
                    if int(time) < cur_time - 20:
                        MonitorQueues.EXCEPTION_TASK.put(task)
                        TDDCLogging.debug(str(index) + ' : '
                                          + task.platform + ' : ' 
                                          + url + ' : '
                                          + str(task.status) + ' : '
                                          + str(time) + ' : '
                                          + 'Crawl Again.')
                        self.hdel(MonitorSite.STATUS_HSET_PREFIX, url)
            gevent.sleep(60)
            TDDCLogging.debug(json.dumps(self._status,
                                         sort_keys=True,
                                         indent=4))

        
def main():
    import gevent.monkey
    gevent.monkey.patch_all()
    StatusManager()
    while True:
        gevent.sleep(10)

if __name__ == '__main__':
    main()
