# encoding: utf-8
"""
@version: ??
@author: chenyitao
@license: Apache Licence 
@software: PyCharm
@file: timing_task_manager.py
@time: 2019-03-01 15:16
"""
import logging
import time
from collections import defaultdict
from os import getpid

import gevent.queue
import six

from ..default_config import default_config
from ..base.util import Singleton
from ..worker import RedisEx, OnlineConfig, EventCenter

from .models.timing_task_model import (
    TimingTask, TimingTaskStatus, TimingTaskIndex, TimingTaskFilterEvent
)
from .models.event_model import Event

log = logging.getLogger(__name__)


@six.add_metaclass(Singleton)
class TimingTaskManager(RedisEx):
    """
    任务管理器
    """

    _totals = 0

    _minutes = 0

    _success = 0

    _one_minute_past_success = 0

    _failed = 0

    _one_minute_past_failed = 0

    def __init__(self):
        """
        Constructor
        """
        self.conf = type('TaskConfig', (), OnlineConfig().task.default)
        self.conf.queue_size = int(self.conf.queue_size)
        super(TimingTaskManager, self).__init__()
        log.info('Task Manager Is Starting.')
        self.filter_table = defaultdict(list)
        self._task_filter_update()
        self._q = gevent.queue.Queue()
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
            if default_config.PID != getpid():
                return
            if int(time.time()) % 60 != 0:
                gevent.sleep(1)
                continue
            current_status = (self._totals, self._success, self._failed)
            if one_minute_past_status == current_status:
                continue
            one_minute_past_status = current_status
            self._minutes += 1
            log.info(fmt % (
                self._totals,
                (self._success + self._failed) / (self._minutes if self._minutes != 0 else 1),
                self._success,
                self._one_minute_past_success,
                self._failed,
                self._one_minute_past_failed)
            )
            self._one_minute_past_success = 0
            self._one_minute_past_failed = 0

    def _pull(self):
        while True:
            if default_config.PID != getpid():
                return
            if self._q.qsize() < self.conf.queue_size:
                try:
                    items = self._pull_task()
                    if not items:
                        gevent.sleep(2)
                        continue
                    tasks = [self._trans_to_task_obj(item) for item in items]
                    tasks = [task for task in tasks
                             if task and not task.filter.filter(self.filter_table)]
                    if len(tasks):
                        for task in tasks:
                            self._totals += 1
                            if task.state == TimingTaskStatus.CrawlTopic:
                                state = TimingTaskStatus.WaitCrawl
                            else:
                                state = TimingTaskStatus.WaitParse
                            task.state.set_state(state)
                            task.recover.start()
                            self._q.put(task)
                        log.info('Pulled New Task({}).'.format(len(tasks)))
                    gevent.sleep(2)
                except Exception as e:
                    log.exception(e)
            else:
                gevent.sleep(2)

    def _pull_task(self):
        topic_base = self.conf.in_queue_topic
        high_weight, middle_weight, low_weight = 0.6, 0.3, 0.1
        share = self.conf.queue_size * 2 - self._q.qsize()
        if share <= 0:
            return []
        task_index = []
        limit = 10
        high_pri_max_share = limit * high_weight
        items = self.pull('{}:{}'.format(topic_base, 'high'), high_pri_max_share) or []
        limit -= (len(items) if items else 0)
        task_index.extend(items)
        middle_pri_max_share = limit * (middle_weight / (middle_weight + low_weight))
        items = self.pull('{}:{}'.format(topic_base, 'middle'), middle_pri_max_share) or []
        limit -= (len(items) if items else 0)
        task_index.extend(items)
        items = self.pull('{}:{}'.format(topic_base, 'low'), limit) or []
        task_index.extend(items)
        return [TimingTaskIndex.init_with_key(index) for index in task_index]

    @staticmethod
    def _trans_to_task_obj(task_index):
        task = TimingTask.init_with_index(task_index)
        return task if task.s_platform and task.s_feature and task.s_url else None

    def get(self, block=True, timeout=None):
        while True:
            if default_config.PID != getpid():
                return
            task = self._q.get(block, timeout)
            if task.filter.filter(self.filter_table):
                continue
            return task

    def put(self, task):
        self._q.put(task)

    def task_success(self, task, the_end=False):
        task.recover.stop()
        if the_end:
            task.destroy()
        else:
            if not task.filter.filter(self.filter_table):
                task.state.set_state(TimingTaskStatus.CrawledSuccess)
                task.cache.set_cache()
                self.push_task(task)
        self._success += 1
        self._one_minute_past_success += 1
        log.debug('[{}:{}:{}] Task Success.'.format(
            task.s_platform, task.s_feature, task.s_url
        ))

    def task_failed(self, task):
        task.filter.filter(self.filter_table)
        task.recover.stop()
        task.destroy()
        self._failed += 1
        self._one_minute_past_failed += 1

        key = '{}:failed:{}:{}'.format(
            self.conf.record_key, task.s_platform, task.s_id
        )
        RedisEx().hmset(key, task.to_dict())

    def push_task(self, task):
        topic = '{}:{}'.format(
            self.conf.out_queue_topic, task.s_priority.lower()
        )

        def _pushed(_):
            log.debug('[{}:{}] Pushed(Topic:{}).'.format(
                task.s_platform, task.s_feature, topic
            ))

        task_index = '{}:{}:{}'.format(
            self.conf.record_key, task.s_platform, task.s_id
        )
        self.push(topic, task_index, _pushed)

    @staticmethod
    @EventCenter.route(TimingTaskFilterEvent)
    def task_filter_update(event):
        ret = TimingTaskManager()._task_filter_update()
        event.set_state(
            Event.Status.Executed_Success if ret else Event.Status.Executed_Failed
        )
        log.info('Task Filter Update.')

    def _task_filter_update(self):
        self.filter_table = defaultdict(list)
        filter_table = RedisEx().hgetall('tddc:task:filter') or {}
        if filter_table:
            for k, v in filter_table.items():
                if not v:
                    continue
                features = v.split(',')
                self.filter_table[k] = features
        return True
