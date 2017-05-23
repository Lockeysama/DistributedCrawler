# -*- coding: utf-8 -*-
'''
Created on 2017年5月8日

@author: chenyitao
'''

import gevent

from conf.default import RedisSite, TaskSite
from common.queues import CrawlerQueues

from plugins import RedisClient


class TaskStatusUpdater(RedisClient):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        super(TaskStatusUpdater, self).__init__(RedisSite.REDIS_NODES)
        gevent.spawn(self._update_task_status)
        gevent.sleep()
        gevent.spawn(self._remove_task_status)
        gevent.sleep()

    def _update_task_status(self):
        while True:
            task = CrawlerQueues.TASK_STATUS.get()
            try:
                self._update(task)
            except Exception, e:
                print('_update_task_status', e)
                CrawlerQueues.TASK_STATUS.put(task)
                gevent.sleep(1)

    def _update(self, task):
        return self.hset(TaskSite.STATUS_HSET_PREFIX + '.%s.%d' % (task.platform, task.status),
                         task.url,
                         task.to_json())

    def _remove_task_status(self):
        while True:
            task = CrawlerQueues.TASK_STATUS_REMOVE.get()
            try:
                self._remove(task)
            except Exception, e:
                print('_update_task_status', e)
                CrawlerQueues.TASK_STATUS_REMOVE.put(task)
                gevent.sleep(1)

    def _remove(self, task):
        return self.hdel(TaskSite.STATUS_HSET_PREFIX + '.%s.%d' % (task.platform, task.status),
                         task.url)


def main():
    pass

if __name__ == '__main__':
    main()
