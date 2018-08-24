# -*- coding: utf-8 -*-
'''
Created on 2017年4月14日

@author: chenyitao
'''
import copy
import logging
from collections import defaultdict

import gevent.queue
import time

import zlib

from .event import EventCenter, Event
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

        Interrupt = 10001

    id = None

    platform = None

    feature = None

    priority = None

    url = None

    method = None

    proxy = None

    space = None

    headers = None

    status = None

    retry = None

    cookies = None

    json = None

    data = None

    is_recovery = True

    response = None

    timestamp = None

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            self.__dict__[k] = v
        self.id = kwargs.get('id', ShortUUID.UUID())
        self.timestamp = kwargs.get('timestamp', int(time.time()))

    def to_dict(self):
        kws = copy.deepcopy(self.__dict__)
        for k, v in kws.items():
            if v is None:
                del kws[k]
        return kws


class TaskRecordManager(RecordManager):
    __metaclass__ = Singleton

    task_conf = DBSession.query(TaskConfigModel).get(1)

    def create_record(self, task):
        """
        创建任务记录
        :param task:
        """
        key = '{base}:{platform}:{task_id}'.format(base=self.task_conf.record_key_base,
                                                   platform=task.platform,
                                                   task_id=task.id)

        def _create_record(_key, _records):
            self.hmset(_key, _records)
        self.robust(_create_record, key, task.to_dict())

    def get_records(self, name):
        """
        获取任务记录
        :param name: 任务索引
        :return:
        """

        def _get_record(_name):
            return self.hgetall(_name)

        task = self.robust(_get_record, name)
        return Task(**task) if task else None

    def delete_record(self, task):
        """
        删除任务记录
        :param task:
        """
        key = '{base}:{platform}:{task_id}'.format(base=self.task_conf.record_key_base,
                                                   platform=task.platform,
                                                   task_id=task.id)

        def _delete_record(_key):
            self.delete(_key)

        self.robust(_delete_record, key)

    def changing_status(self, task):
        """
        更改任务状态
        :param task:
        """
        key = '{base}:{platform}:{task_id}'.format(base=self.task_conf.record_key_base,
                                                   platform=task.platform,
                                                   task_id=task.id)

        def _changing_status(_key, _status):
            self.set_record_item_value(_key, 'status', _status)
        self.robust(_changing_status, key, task.status)

    def start_task_timer(self, task, count=300):
        """
        设置任务回收倒计时
        :param task:
        :param count:
        """
        if not task.is_recovery:
            return
        task_index = 'tddc:task:record:{}:{}:countdown'.format(task.platform, task.id)

        def _start_task_timer(_task_index, _count, _status):
            self.setex(_task_index, _count, _status)
        self.robust(_start_task_timer, task_index, count, task.status)

    def stop_task_timer(self, task):
        """
        取消任务回收倒计时
        :param task:
        """
        if not task.is_recovery:
            return
        task_index = 'tddc:task:record:{}:{}:countdown'.format(task.platform, task.id)

        def _stop_task_timer(_task_index):
            self.delete(_task_index)
        self.robust(_stop_task_timer, task_index)


class TaskCacheManager(CacheManager):
    __metaclass__ = Singleton

    task_conf = DBSession.query(TaskConfigModel).get(1)

    def set_cache(self, task, content):
        """
        设置任务缓存
        :param task:
        :param content:
        """
        key = '{base}:{platform}'.format(base=self.task_conf.cache_key_base,
                                         platform=task.platform)
        cmp_content = zlib.compress(content)

        def _set_cache(_key, _task, _content):
            ret = self.hset(_key, _task.id, _content)
            return ret
        return self.robust(_set_cache, key, task, cmp_content)

    def get_cache(self, task):
        """
        获取任务缓存
        :param task:
        :return:
        """
        key = '{base}:{platform}'.format(base=self.task_conf.cache_key_base,
                                         platform=task.platform)

        def _get_cache(_key, _task):
            return self.hget(key, _task.id)
        cmp_content = self.robust(_get_cache, key, task)
        content = zlib.decompress(cmp_content) if cmp_content else None
        return content

    def delete_cachce(self, task):
        key = '{base}:{platform}'.format(base=self.task_conf.cache_key_base,
                                         platform=task.platform)

        def _delete_cache(_key, _task):
            return self.hdel(_key, _task.id)
        return self.robust(_delete_cache, key, task)


class TaskManager(MessageQueue):
    '''
    任务管理器
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
        self.filter_table = defaultdict(list)
        self._task_filter_update()
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
        while True:
            if self._q.qsize() < self.task_conf.max_queue_size:
                items = self._pull_task_old()
                items.extend(self._pull_task())
                if not items:
                    gevent.sleep(2)
                    continue
                tasks = [self._trans_to_task_obj(item) for item in items]
                tasks = [task for task in tasks if task and task.platform and task.feature and task.url]
                if len(tasks):
                    for task in tasks:
                        if self.task_filter(task):
                            continue
                        self._totals += 1
                        task.status = Task.Status.WaitCrawl \
                            if self.worker.platform == 'crawler' \
                            else Task.Status.WaitParse
                        TaskRecordManager().changing_status(task)
                        TaskRecordManager().start_task_timer(task)
                        self._q.put(task)
                    log.info('Pulled New Task({}).'.format(len(tasks)))
                gevent.sleep(2)
            else:
                gevent.sleep(2)

    def _pull_task_old(self):
        topic = self.task_conf.crawler_topic \
            if self.worker.platform == 'crawler' \
            else self.task_conf.parser_topic
        items = self.pull(topic, self.task_conf.max_queue_size)
        return items or []

    def _pull_task(self):
        topic_base = self.task_conf.crawler_topic \
            if self.worker.platform == 'crawler' \
            else self.task_conf.parser_topic
        high_weight, middle_weight, low_weight = 0.5, 0.35, 0.15
        share = self.task_conf.max_queue_size * 2 - self._q.qsize()
        if share <= 0:
            return []
        tasks = []
        topic = '{}:{}'.format(topic_base, 'high')
        high_pri_max_share = share * high_weight
        items = self.pull(topic, high_pri_max_share) or []
        share -= (len(items) if items else 0)
        tasks.extend(items)
        topic = '{}:{}'.format(topic_base, 'middle')
        middle_pri_max_share = share * (middle_weight / (middle_weight + low_weight))
        items = self.pull(topic, middle_pri_max_share) or []
        share -= (len(items) if items else 0)
        tasks.extend(items)
        topic = '{}:{}'.format(topic_base, 'low')
        items = self.pull(topic, share) or []
        tasks.extend(items)
        return tasks

    @staticmethod
    def _trans_to_task_obj(task_index):
        return TaskRecordManager().get_records(task_index) or None

    def get(self, block=True, timeout=None):
        while True:
            task = self._q.get(block, timeout)
            if self.task_filter(task):
                continue
            return task

    def put(self, task):
        self._q.put(task)

    def task_success(self, task):
        if self.task_filter(task):
            TaskRecordManager().stop_task_timer(task)
            log.debug('[{}:{}:{}] Task Filter.'.format(
                task.platform, task.feature, task.url
            ))
            return False
        self._success += 1
        self._one_minute_past_success += 1
        TaskRecordManager().changing_status(task)
        TaskRecordManager().stop_task_timer(task)
        log.debug('[{}:{}:{}] Task Success.'.format(
            task.platform, task.feature, task.url
        ))
        return True

    def task_successed(self, task):
        return self.task_success(task)

    def task_failed(self, task):
        TaskRecordManager().delete_record(task)
        if self.task_filter(task):
            TaskRecordManager().stop_task_timer(task)
            log.debug('[{}:{}:{}] Task Filter.'.format(
                task.platform, task.feature, task.url
            ))
            return
        self._failed += 1
        self._one_minute_past_failed += 1
        TaskRecordManager().stop_task_timer(task)
        log.warning('[{}:{}:{}] Task Failed({}).'.format(
            task.platform, task.feature, task.url, task.status
        ))

    def push_task(self, task, topic):
        if self.task_filter(task):
            TaskRecordManager().stop_task_timer(task)
            log.debug('[{}:{}:{}] Task Filter.'.format(
                task.platform, task.feature, task.url
            ))
            return

        if not hasattr(task, 'priority') or not task.priority:
            def _pushed(_):
                log.debug('[{}:{}] Pushed(Topic:{}).'.format(
                    task.platform, task.feature, topic
                ))

            task_index = 'tddc:task:record:{}:{}'.format(task.platform, task.id)
            self.push(topic, task_index, _pushed)
        else:
            topic = '{}:{}'.format(topic, task.priority)

            def _pushed(_):
                log.debug('[{}:{}] Pushed(Topic:{}).'.format(
                    task.platform, task.feature, topic
                ))

            task_index = 'tddc:task:record:{}:{}'.format(task.platform, task.id)
            self.push(topic, task_index, _pushed)

    @staticmethod
    @EventCenter.route(Event.Type.TaskFilterUpdate)
    def task_filter_update(event):
        EventCenter().update_the_status(event,
                                        Event.Status.Executed_Success
                                        if TaskManager()._task_filter_update()
                                        else Event.Status.Executed_Failed)
        log.info('Task Filter Update.')

    def _task_filter_update(self):
        self.filter_table = defaultdict(list)
        filter_table = RecordManager().hgetall('tddc:task:filter') or {}
        if filter_table:
            for k, v in filter_table.items():
                if not v:
                    continue
                features = v.split(',')
                self.filter_table[k] = features
        return True

    def task_filter(self, task):
        filter_features = self.filter_table.get(task.platform)
        if filter_features:
            if task.feature in filter_features:
                TaskRecordManager().delete_record(task)
                return True
        return False
