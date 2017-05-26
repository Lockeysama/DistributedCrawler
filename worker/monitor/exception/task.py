# -*- coding: utf-8 -*-
'''
Created on 2017年5月17日

@author: chenyitao
'''

import gevent

from common.models import Task
from common.queues_define import TASK_STATUS_REMOVE_QUEUE, EXCEPTION_TASK_QUEUE
from conf.base_site import PARSE_TOPIC_NAME, CRAWL_TOPIC_NAME

from .. import TaskManagerBase
from log import TDDCLogging


class ExceptionTaskManager(TaskManagerBase):
    '''
    classdocs
    '''
    
    topics = {}

    def __init__(self):
        '''
        Constructor
        '''
        TDDCLogging.info('--->Task Manager Is Starting.')
        super(ExceptionTaskManager, self).__init__()
        self._status_task_table = {Task.Status.WAIT_CRAWL: CRAWL_TOPIC_NAME,
                                   Task.Status.WAIT_PARSE: PARSE_TOPIC_NAME}
        gevent.spawn(self._push)
        gevent.sleep()
        TDDCLogging.info('--->Task Manager Was Ready.')
    
    def _push(self):
        TDDCLogging.info('---->Task Producer Was Ready.')
        while True:
            task = EXCEPTION_TASK_QUEUE.get()
            print(task.__dict__)
            continue
            if not isinstance(task, Task):
                TDDCLogging.error('')
                continue
            if not self._push_task(self._status_task_table.get(task.status, None), task):
                TDDCLogging.error('')
                EXCEPTION_TASK_QUEUE.put(task)
                gevent.sleep(1)
            else:
                TASK_STATUS_REMOVE_QUEUE.put(task)
                TDDCLogging.debug('[%s:%s] Task Redistribution Successed.' % (task.platform,
                                                                              task.url))
                self._successed_num += 1
                self._successed_pre_min += 1


def main():
    import gevent.monkey
    gevent.monkey.patch_all()
    
    ExceptionTaskManager()
    while True:
        gevent.sleep(1)

if __name__ == '__main__':
    main()