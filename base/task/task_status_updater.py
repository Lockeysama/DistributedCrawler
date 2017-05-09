# -*- coding: utf-8 -*-
'''
Created on 2017年5月8日

@author: chenyitao
'''
from plugins.rsm.redis_manager.remote_shared_memory import RedisClient
import gevent
from conf.base_site import STATUS, TASK_STATUS_HSET
from common.queues import TASK_STATUS_QUEUE, TASK_STATUS_REMOVE_QUEUE
import time

class TaskStatusUpdater(object):
    '''
    classdocs
    '''

    def __init__(self, redis_client=None):
        '''
        Constructor
        '''
        self._redis_client = redis_client
        if not redis_client:
            self._redis_client = RedisClient()
        self._rdm = self._redis_client._rdm
        gevent.spawn(self._update_task_status)
        gevent.sleep()
        gevent.spawn(self._remove_task_status)
        gevent.sleep()

    def _update_task_status(self):
        while STATUS:
            task = TASK_STATUS_QUEUE.get()
            try:
                self._update(task)
            except Exception, e:
                print('_update_task_status', e)
                TASK_STATUS_QUEUE.put(task)
                gevent.sleep(1)

    def _update(self, task):
        return self._rdm.hset(TASK_STATUS_HSET, task.url, '%d,%d' % (task.status, time.time()))
    
    def _remove_task_status(self):
        while STATUS:
            task = TASK_STATUS_REMOVE_QUEUE.get()
            try:
                self._remove(task)
            except Exception, e:
                print('_update_task_status', e)
                TASK_STATUS_REMOVE_QUEUE.put(task)
                gevent.sleep(1)

    def _remove(self, task):
        return self._rdm.hdel(TASK_STATUS_HSET, task.url)
    
            
def main():
    pass

if __name__ == '__main__':
    main()
