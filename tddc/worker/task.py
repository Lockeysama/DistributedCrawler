# -*- coding: utf-8 -*-
'''
Created on 2017年4月14日

@author: chenyitao
'''

import gevent

from ..kafka.consumer import KeepAliveConsumer
from ..util.util import Singleton, object2json

from .worker_config import WorkerConfigCenter
from .status import StatusManager
from .postman import Postman


class TaskStatus(object):
    CrawlTopic = 0

    WaitCrawl = 1
    CrawledSuccess = 200
    # CrawledFailed : 错误码为HTTP Response Status

    WaitParse = 1001
    ParseModuleNotFound = 1100
    ParsedSuccess = 1200
    ParsedFailed = 1400

    @classmethod
    def next_status(cls, state):
        status = [cls.CrawlTopic,
                  cls.WaitCrawl,
                  cls.CrawledSuccess,
                  cls.WaitParse,
                  cls.ParseModuleNotFound,
                  cls.ParsedSuccess,
                  cls.ParsedFailed]
        index = status.index(state)
        if index < 0:
            return cls.WaitCrawl
        if index == len(status) - 1:
            return cls.ParsedFailed
        return status[index + 1]


class Task(object):

    timestamp = 0

    interval = 120

    cur_status = 0

    pre_status = 0


class TaskManager(KeepAliveConsumer):
    '''
    classdocs
    '''
    __metaclass__ = Singleton

    def __init__(self):
        '''
        Constructor
        '''
        self.task_conf = WorkerConfigCenter().get_task()
        kafka_info = WorkerConfigCenter().get_kafka()
        if not kafka_info:
            self.error('Kafka Server Info Not Found.')
            return
        kafka_nodes = ','.join(['%s:%s' % (info.host, info.port) for info in kafka_info])
        super(TaskManager, self).__init__(self.task_conf.consumer_topic,
                                          self.task_conf.consumer_group,
                                          self.task_conf.local_task_queue_size,
                                          bootstrap_servers=kafka_nodes)
        self.info('Task Manager Is Starting.')
        self._totals = 0
        self._minutes = 0
        self._success = 0
        self._one_minute_past_success = 0
        self._failed = 0
        self._one_minute_past_failed = 0
        gevent.spawn(self._counter)
        gevent.sleep()
        self.info('Task Manager Was Ready.')

    def _counter(self):
        fmt = ('\n'
               '********* Task Status *********\n'
               '-> Totals: %d\n'
               '-> Average: %d\n'
               '-> Success: %d\n'
               '-> OneMinutePastSuccess: %d\n'
               '-> Failed: %d\n'
               '-> OneMinutePastFailed: %d\n'
               '*******************************\n')
        one_minute_past_status = tuple()
        while True:
            gevent.sleep(60)
            current_status = (self._totals,
                              self._success,
                              self._failed)
            if one_minute_past_status == current_status:
                continue
            one_minute_past_status = current_status
            self._minutes += 1
            self.info(fmt % (self._totals,
                             (self._success + self._failed) / (self._minutes if self._minutes != 0 else 1),
                             self._success,
                             self._one_minute_past_success,
                             self._failed,
                             self._one_minute_past_failed))
            self._one_minute_past_success = 0
            self._one_minute_past_failed = 0

    def _record_fetched(self, item):
        task = item
        if not hasattr(task, 'id') or not hasattr(task, 'cur_status'):
            return
        task.pre_status = task.cur_status
        task.cur_status = (TaskStatus.WaitCrawl
                           if task.cur_status == TaskStatus.CrawlTopic
                           else TaskStatus.WaitParse)
        self.task_status_changed(task)
        self._totals += 1

    def _deserialization(self, item):
        return type('TaskRecord', (Task,), item)

    def get(self, block=True, timeout=None):
        task = super(TaskManager, self).get(block, timeout)
        return task

    def task_status_changed(self, task):
        StatusManager().update_status('{base}:{platform}'.format(base=self.task_conf.status_key_base,
                                                                 platform=task.platform),
                                      task.id,
                                      task.cur_status,
                                      task.pre_status)

    def task_successed(self, task):
        self._success += 1
        self._one_minute_past_success += 1
        self.task_status_changed(task)
        self.debug('[%s:%s:%s] Task Success.' % (task.platform,
                                                 task.id,
                                                 task.url))

    def task_failed(self, task):
        self._failed += 1
        self._one_minute_past_failed += 1
        self.task_status_changed(task)
        self.warning('[%s:%s:%s] Task Failed(%d).' % (task.platform,
                                                      task.id,
                                                      task.url,
                                                      task.cur_status))

    def push_task(self, task, topic, status_update=True):
        def _pushed(_):
            if status_update:
                self.task_status_changed(task)
            self.debug('[%s:%s] Pushed(Topic:%s).' % (task.platform,
                                                      task.id,
                                                      topic))

        Postman().push(topic, object2json(task), _pushed)
