# -*- coding: utf-8 -*-
'''
Created on 2017年7月3日

@author: chenyitao
'''

import time

from common.models.exception.base import ExceptionType
from common.models.task import Task
from common.queues.monitor import MonitorQueues
from conf.monitor_site import MonitorSite


class CrawlerClientEP(object):
    '''
    Crawler Client Exception Process.
    '''

    EXCEPTION_TYPE = ExceptionType.Crawler.CLIENT

    def __init__(self, exception):
        self._exception = exception


class CrawlerTaskEP(object):
    '''
    Crawler Task Exception Process.
    '''

    EXCEPTION_TYPE = ExceptionType.Crawler.TASK_FAILED

    def __init__(self, exception):
        self._exception = exception
        self._processing()

    def _processing(self):
        task = Task(**self._exception.task)
        if task.status == Task.Status.WAIT_CRAWL:
            task.timestamp = time.time()
            MonitorQueues.EXCEPTION_TASK.put((MonitorSite.CRAWL_TOPIC, task))
