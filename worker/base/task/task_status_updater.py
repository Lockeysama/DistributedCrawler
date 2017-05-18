# -*- coding: utf-8 -*-
'''
Created on 2017年5月8日

@author: chenyitao
'''

import gevent

from conf.base_site import TASK_STATUS_HSET, REDIS_NODES
from common.queues import TASK_STATUS_QUEUE, TASK_STATUS_REMOVE_QUEUE

from plugins import RedisClient


class TaskStatusUpdater(RedisClient):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        super(TaskStatusUpdater, self).__init__(REDIS_NODES)
        gevent.spawn(self._update_task_status)
        gevent.sleep()
        gevent.spawn(self._remove_task_status)
        gevent.sleep()

    def _update_task_status(self):
        while True:
            task = TASK_STATUS_QUEUE.get()
            try:
                self._update(task)
            except Exception, e:
                print('_update_task_status', e)
                TASK_STATUS_QUEUE.put(task)
                gevent.sleep(1)

    def _update(self, task):
        return self.hset(TASK_STATUS_HSET + '.%s.%d' % (task.platform, task.status),
                         task.url,
                         task.to_json())

    def _remove_task_status(self):
        while True:
            task = TASK_STATUS_REMOVE_QUEUE.get()
            try:
                self._remove(task)
            except Exception, e:
                print('_update_task_status', e)
                TASK_STATUS_REMOVE_QUEUE.put(task)
                gevent.sleep(1)

    def _remove(self, task):
        return self.hdel(TASK_STATUS_HSET + '.%s.%d' % (task.platform, task.status),
                         task.url)


def main():
    pass

if __name__ == '__main__':
    main()
