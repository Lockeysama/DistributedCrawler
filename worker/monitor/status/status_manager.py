# -*- coding: utf-8 -*-
'''
Created on 2017年5月17日

@author: chenyitao
'''

import gevent
import json
import time

from conf.base_site import TASK_STATUS_HSET, REDIS_NODES
from log import TDDCLogging
from common.models.task import Task
from common.queues_define import EXCEPTION_TASK_QUEUE
from plugins import RedisClient


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
        super(StatusManager, self).__init__(REDIS_NODES)
        gevent.spawn(self._get_status)
        gevent.sleep()
        TDDCLogging.info('-->Status Manager Was Started.')
    
    def _get_status(self):
        while True:
            cur_time = 1495087998  # time.time()
            keys = self._rdm.keys(TASK_STATUS_HSET + '.*')
            for key in keys:
                h_len = self._rdm.hlen(key)
                platform, status = key.split('.')[-2:]
                if not self._status.get(platform):
                    self._status[platform] = {}
                self._status[platform][status] = h_len
                item = self._rdm.hscan_iter(key)
                for index, (url, task) in enumerate(item):
                    task = json.loads(task)
                    task = Task(**task)
                    time = task.timestamp
                    if int(time) < cur_time - 20:
                        EXCEPTION_TASK_QUEUE.put(task)
                        TDDCLogging.debug(str(index) + ' : '
                                          + task.platform + ' : ' 
                                          + url + ' : '
                                          + str(task.status) + ' : '
                                          + str(time) + ' : '
                                          + 'Crawl Again.')
    #                     self._rdm.hdel(TASK_STATUS_HSET, time_url)
            gevent.sleep(60)
            TDDCLogging.debug(json.dumps(self._status))

        
def main():
    import gevent.monkey
    gevent.monkey.patch_all()
    StatusManager()
    while True:
        gevent.sleep(10)

if __name__ == '__main__':
    main()
