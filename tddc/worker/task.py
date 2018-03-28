# -*- coding: utf-8 -*-
'''
Created on 2017年4月14日

@author: chenyitao
'''
import logging
import gevent.queue
import time

from .models import TaskConfigModel, DBSession, WorkerModel
from .record import RecordManager
from .cache import CacheManager
from .message_queue import MessageQueue

from ..util.util import Singleton
from ..util.short_uuid import ShortUUID

log = logging.getLogger(__name__)


class Task(object):
    class Status(object):
        CrawlTopic = 0

        WaitCrawl = 1
        CrawledSuccess = 200
        # CrawledFailed : 错误码为HTTP Response Status

        WaitParse = 1001
        ParseModuleNotFound = 1100
        ParsedSuccess = 1200
        ParsedFailed = 1400

    id = None

    platform = None

    feature = None

    url = None

    method = None

    proxy = None

    space = None

    headers = None

    status = None

    timestamp = None

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            self.__dict__[k] = v
        self.id = kwargs.get('id', ShortUUID.UUID())
        self.timestamp = kwargs.get('timestamp', int(time.time()))

    def to_dict(self):
        return self.__dict__


class TaskRecordManager(RecordManager):
    __metaclass__ = Singleton

    task_conf = DBSession.query(TaskConfigModel).get(1)

    def create_record(self, task):
        key = '{base}:{platform}:{task_id}'.format(base=self.task_conf.record_key_base,
                                                   platform=task.platform,
                                                   task_id=task.id)

        def _create_record(_name, _key, _record):
            self.hset(_name, _key, _record)
        self.robust(_create_record, key, task.id, task.to_dict())

    def get_records(self, name):
        def _get_record(_name):
            return self.hgetall(_name)

        task = self.robust(_get_record, name)
        return Task(**task) if task else None

    def changing_status(self, task):
        key = '{base}:{platform}:{task_id}'.format(base=self.task_conf.record_key_base,
                                                   platform=task.platform,
                                                   task_id=task.id)
        self.set_record_item_value(key, 'status', task.status)

    def start_task_timer(self, task, count=300):
        task_index = 'tddc:task:record:{}:{}:countdown'.format(task.platform, task.id)
        self.setex(task_index, count, task.status)


class TaskCacheManager(CacheManager):
    __metaclass__ = Singleton

    task_conf = DBSession.query(TaskConfigModel).get(1)

    def set_cache(self, task, content):
        key = '{base}:{platform}'.format(base=self.task_conf.cache_key_base,
                                         platform=task.platform)
        self.hset(key, task.id, content)

    def get_cache(self, task):
        key = '{base}:{platform}'.format(base=self.task_conf.cache_key_base,
                                         platform=task.platform)
        return self.hget(key, task.id)


class TaskManager(MessageQueue):
    '''
    classdocs
    '''
    __metaclass__ = Singleton

    def __init__(self, mode='normal'):
        '''
        Constructor
        '''
        self.task_conf = DBSession.query(TaskConfigModel).get(1)
        self.worker = DBSession.query(WorkerModel).get(1)
        super(TaskManager, self).__init__()
        log.info('Task Manager Is Starting.')
        self._totals = 0
        self._minutes = 0
        self._success = 0
        self._one_minute_past_success = 0
        self._failed = 0
        self._one_minute_past_failed = 0
        self._q = gevent.queue.Queue()
        if mode == 'normal':
            gevent.spawn(self._counter)
            gevent.sleep()
            gevent.spawn(self._pull)
            gevent.sleep()
        log.info('Task Manager Was Ready.')

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
            log.info(fmt % (self._totals,
                            (self._success + self._failed) / (self._minutes if self._minutes != 0 else 1),
                            self._success,
                            self._one_minute_past_success,
                            self._failed,
                            self._one_minute_past_failed))
            self._one_minute_past_success = 0
            self._one_minute_past_failed = 0

    def _pull(self):
        topic = self.task_conf.crawler_topic \
            if self.worker.platform == 'crawler' \
            else self.task_conf.parser_topic
        while True:
            if self._q.qsize() < self.task_conf.max_queue_size:
                items = self.pull(topic,
                                  self.task_conf.max_queue_size)
                if not items:
                    gevent.sleep(2)
                    continue
                tasks = [self._trans_to_task_obj(item) for item in items]
                tasks = [task for task in tasks if task.platform and task.feature and task.url]
                for task in tasks:
                    self._q.put(task)
                log.info('Pulled New Task(%d).' % len(tasks))
                gevent.sleep(2)
            else:
                gevent.sleep(2)

    def _trans_to_task_obj(self, task_index):
        task = TaskRecordManager().get_records(task_index)
        task.status = Task.Status.WaitCrawl \
            if self.worker.platform == 'crawler' \
            else Task.Status.WaitParse
        TaskRecordManager().changing_status(task)
        TaskRecordManager().start_task_timer(task)
        self._totals += 1
        return task

    def get(self, block=True, timeout=None):
        task = self._q.get(block, timeout)
        return task

    def task_successed(self, task):
        self._success += 1
        self._one_minute_past_success += 1
        TaskRecordManager().changing_status(task)
        log.debug('[%s:%s:%s] Task Success.' % (task.platform,
                                                task.id,
                                                task.url))

    def task_failed(self, task):
        self._failed += 1
        self._one_minute_past_failed += 1
        TaskRecordManager().changing_status(task)
        log.warning('[%s:%s:%s] Task Failed(%s).' % (task.platform,
                                                     task.id,
                                                     task.url,
                                                     task.status))

    def push_task(self, task, topic):
        def _pushed(_):
            log.debug('[%s:%s] Pushed(Topic:%s).' % (task.platform,
                                                     task.id,
                                                     topic))

        task_index = 'tddc:task:record:{}:{}'.format(task.platform, task.id)
        self.push(topic, task_index, _pushed)
