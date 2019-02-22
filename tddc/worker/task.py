# -*- coding: utf-8 -*-
"""
Created on 2017年4月14日

@author: chenyitao
"""
import logging
import random
import time
from collections import defaultdict
from os import getpid
from string import lower

import gevent.queue

from ..base.util import Singleton, JsonObjectSerialization, SnowFlakeID
from ..default_config import default_config

from event import EventCenter, Event
from online_config import OnlineConfig
from redisex import RedisEx

log = logging.getLogger(__name__)


class Task(JsonObjectSerialization):
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

    fields = [
        's_id', 's_url', 's_platform', 's_feature', 'i_status', 'i_space', 's_headers',
        's_method', 's_proxy', 's_data', 's_cookies', 's_params', 's_json', 's_priority',
        'b_allow_redirects', 'b_interrupt', 'b_valid', 'b_is_recover', 'i_timestamp',
        's_start_date', 's_timer', 's_desc'
    ]

    def __init__(self, fields=None, **kwargs):
        super(Task, self).__init__(fields, **kwargs)
        self.s_id = kwargs.get('s_id', SnowFlakeID().get_id())
        self.i_timestamp = kwargs.get('i_timestamp', int(time.time()))


class TaskManager(RedisEx):
    """
    任务管理器
    """
    __metaclass__ = Singleton

    def __init__(self, mode='normal'):
        """
        Constructor
        """
        self.task_conf = type('TaskConfig', (), OnlineConfig().task.default)
        self.task_conf.queue_size = int(self.task_conf.queue_size)
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
            if default_config.PID != getpid():
                return
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
            if default_config.PID != getpid():
                return
            if self._q.qsize() < self.task_conf.queue_size:
                items = self._pull_task_old()
                items.extend(self._pull_task())
                if not items:
                    gevent.sleep(2)
                    continue
                tasks = [self._trans_to_task_obj(item) for item in items]
                tasks = [task for task in tasks if task and task.s_platform and task.s_feature and task.s_url]
                if len(tasks):
                    for task in tasks:
                        if self.task_filter(task):
                            continue
                        self._totals += 1
                        task.i_status = Task.Status.WaitCrawl \
                            if lower(default_config.PLATFORM) == 'crawler' \
                            else Task.Status.WaitParse
                        key = '{base}:{platform}:{task_id}'.format(
                            base=self.task_conf.record_key,
                            platform=task.s_platform,
                            task_id=task.s_id
                        )
                        RedisEx().set_record_item_value(key, 'status', task.i_status)
                        if task.b_is_recover:
                            task_index = 'tddc:task:record:{}:{}:countdown'.format(task.s_platform, task.s_id)
                            RedisEx().setex(task_index, 300, task.i_status)
                        self._q.put(task)
                    log.info('Pulled New Task({}).'.format(len(tasks)))
                gevent.sleep(2)
            else:
                gevent.sleep(2)

    def _pull_task_old(self):
        topic = self.task_conf.in_queue_topic
        items = self.pull(topic, random.randint(1, 5))
        return items or []

    def _pull_task(self):
        topic_base = self.task_conf.in_queue_topic
        high_weight, middle_weight, low_weight = 0.6, 0.3, 0.1
        share = self.task_conf.queue_size * 2 - self._q.qsize()
        if share <= 0:
            return []
        tasks = []
        limit = 10
        topic = '{}:{}'.format(topic_base, 'high')
        high_pri_max_share = limit * high_weight
        items = self.pull(topic, high_pri_max_share) or []
        limit -= (len(items) if items else 0)
        tasks.extend(items)
        topic = '{}:{}'.format(topic_base, 'middle')
        middle_pri_max_share = limit * (middle_weight / (middle_weight + low_weight))
        items = self.pull(topic, middle_pri_max_share) or []
        limit -= (len(items) if items else 0)
        tasks.extend(items)
        topic = '{}:{}'.format(topic_base, 'low')
        items = self.pull(topic, limit) or []
        tasks.extend(items)
        return tasks

    @staticmethod
    def _trans_to_task_obj(task_index):
        return Task(**RedisEx().get_records(task_index)) or None

    def get(self, block=True, timeout=None):
        while True:
            if default_config.PID != getpid():
                return
            task = self._q.get(block, timeout)
            if self.task_filter(task):
                continue
            return task

    def put(self, task):
        self._q.put(task)

    def task_success(self, task, the_end=False):
        if self.task_filter(task):
            if not task.b_is_recover:
                return
            task_index = 'tddc:task:record:{}:{}:countdown'.format(task.s_platform, task.s_id)
            RedisEx().delete(task_index)
            log.debug('[{}:{}:{}] Task Filter.'.format(
                task.s_platform, task.s_feature, task.s_url
            ))
            return False
        self._success += 1
        self._one_minute_past_success += 1
        key = '{base}:{platform}:{task_id}'.format(base=self.task_conf.record_key,
                                                   platform=task.s_platform,
                                                   task_id=task.s_id)
        RedisEx().set_record_item_value(key, 'status', task.i_status)
        task_index = 'tddc:task:record:{}:{}:countdown'.format(task.s_platform, task.s_id)
        RedisEx().delete(task_index)
        log.debug('[{}:{}:{}] Task Success.'.format(
            task.s_platform, task.s_feature, task.s_url
        ))
        if the_end:
            key = '{base}:{platform}'.format(base=self.task_conf.cache_key,
                                             platform=task.s_platform)
            RedisEx().hdel(key, task.s_id)
            key = '{base}:{platform}:{task_id}'.format(base=self.task_conf.record_key,
                                                       platform=task.s_platform,
                                                       task_id=task.s_id)
            RedisEx().delete(key)
        return True

    def task_successed(self, task, the_end=False):
        return self.task_success(task, the_end)

    def task_failed(self, task):
        key = '{base}:{platform}:{task_id}'.format(base=self.task_conf.record_key,
                                                   platform=task.s_platform,
                                                   task_id=task.s_id)
        RedisEx().delete(key)
        if self.task_filter(task):
            task_index = 'tddc:task:record:{}:{}:countdown'.format(task.s_platform, task.s_id)
            RedisEx().delete(task_index)
            log.debug('[{}:{}:{}] Task Filter.'.format(
                task.s_platform, task.s_feature, task.s_url
            ))
            return
        self._failed += 1
        self._one_minute_past_failed += 1
        task_index = 'tddc:task:record:{}:{}:countdown'.format(task.s_platform, task.s_id)
        RedisEx().delete(task_index)
        log.warning('[{}:{}:{}] Task Failed({}).'.format(
            task.s_platform, task.s_feature, task.s_url, task.i_status
        ))
        RedisEx().sadd(
            'tddc:task:failed:{}:{}:{}'.format(
                task.s_platform, task.s_feature, task.i_status
            ),
            task.s_url
        )
        key = '{base}:{platform}'.format(base=self.task_conf.cache_key,
                                         platform=task.s_platform)
        RedisEx().hdel(key, task.s_id)
        key = '{base}:{platform}:{task_id}'.format(base=self.task_conf.record_key,
                                                   platform=task.s_platform,
                                                   task_id=task.s_id)
        RedisEx().delete(key)

    def push_task(self, task, topic):
        if self.task_filter(task):
            task_index = 'tddc:task:record:{}:{}:countdown'.format(task.s_platform, task.s_id)
            RedisEx().delete(task_index)
            log.debug('[{}:{}:{}] Task Filter.'.format(
                task.s_platform, task.s_feature, task.s_url
            ))
            return

        if not hasattr(task, 's_priority') or not task.s_priority:
            def _pushed(_):
                log.debug('[{}:{}] Pushed(Topic:{}).'.format(
                    task.s_platform, task.s_feature, topic
                ))

            task_index = 'tddc:task:record:{}:{}'.format(task.s_platform, task.s_id)
            self.push(topic, task_index, _pushed)
        else:
            topic = '{}:{}'.format(topic, task.s_priority.lower())

            def _pushed(_):
                log.debug('[{}:{}] Pushed(Topic:{}).'.format(
                    task.s_platform, task.s_feature, topic
                ))

            task_index = 'tddc:task:record:{}:{}'.format(task.s_platform, task.s_id)
            self.push(topic, task_index, _pushed)

    @staticmethod
    @EventCenter.route(Event.Type.TaskFilterUpdate)
    def task_filter_update(event):
        EventCenter().update_the_status(
            event,
            Event.Status.Executed_Success
            if TaskManager()._task_filter_update()
            else Event.Status.Executed_Failed
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

    def task_filter(self, task):
        filter_features = self.filter_table.get(task.s_platform)
        if filter_features:
            if task.s_feature in filter_features:
                key = '{base}:{platform}:{task_id}'.format(base=self.task_conf.record_key,
                                                           platform=task.s_platform,
                                                           task_id=task.s_id)
                RedisEx().delete(key)
                return True
        return False
