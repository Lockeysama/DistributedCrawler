# encoding: utf-8
"""
@version: ??
@author: chenyitao
@license: Apache Licence 
@software: PyCharm
@file: helper.py
@time: 2018/3/27 19:47
"""
import json
import logging
import random
from collections import defaultdict

import gevent
import time

import six
from ......base.util import Singleton, ShortUUID, SnowFlakeID
from ......worker import (
    Event, TimingTask, KeepTask, OnlineConfig, TimingTaskStatus,
    KeepTaskStatus, KeepTaskEvent
)

from ......worker.redisex import RedisEx

log = logging.getLogger(__name__)

EVENT_All_TASK_FILTER_UPDATE = 2001


@six.add_metaclass(Singleton)
class TaskHelper(object):

    key_base = 'tddc:task:config:timing'

    def __init__(self):
        log.info('Task Helper Starting.')
        super(TaskHelper, self).__init__()
        self._status = {}
        self.filter_table = defaultdict(list)
        self.task_config = type('TaskConfig', (), OnlineConfig().task.default)
        self.event_config = type('EventConfig', (), OnlineConfig().event.default)
        self.task_filter_update()
        gevent.spawn(self._main_task_manager)
        gevent.sleep()
        gevent.spawn(self._task_recycle)
        gevent.sleep()
        log.info('Task Helper Was Ready.')

    def edit(self, task):
        data = task.to_dict()
        name = '{}:{}'.format(self.key_base, task.s_feature)
        RedisEx().hmset(name, data)

    def delete(self, feature):
        RedisEx().delete(
            '{}:{}'.format(self.key_base, feature)
        )

    def query(self, feature='*'):
        if feature == '*':
            keys = RedisEx().keys('{}:*'.format(self.key_base))
            return [TimingTask(**RedisEx().hgetall(key)) for key in keys]
        else:
            key = RedisEx().keys('{}:{}'.format(
                self.key_base, feature)
            )
            if key:
                key = key[0]
            return TimingTask(**RedisEx().hgetall(key))

    def task_filter_update(self):
        filter_table = RedisEx().hgetall('tddc:task:filter') or {}
        if filter_table:
            for k, v in filter_table.items():
                if not v:
                    continue
                features = v.split(',')
                self.filter_table[k] = features

    def task_filter(self, task):
        filter_features = self.filter_table.get(task.s_platform)
        if filter_features:
            if task.s_feature in filter_features:
                key = '{base}:{platform}:{task_id}'.format(
                    base=self.task_config.record_key, platform=task.s_platform, task_id=task.s_id
                )
                RedisEx().delete(key)
                return True
        return False

    def _main_task_manager(self):
        """
        Get Task Info From Redis
        :return:
        """
        self.main_tasks_id = set()
        while True:
            try:
                self._fetch_main_task()
            except Exception as e:
                log.exception(e)
                log.warning(e.message)
            gevent.sleep(10)

    def _fetch_main_task(self):
        tasks = self.query()
        cur_time = int(time.time())
        for task in tasks:
            if not task.b_valid \
                    or ((cur_time - task.i_timestamp) < task.i_space) \
                    or task.b_interrupt:
                continue
            task.i_timestamp = cur_time
            task.i_state = TimingTaskStatus.CrawlTopic
            key = '{base}:{platform}:{task_id}'.format(
                base=self.task_config.record_key, platform=task.s_platform, task_id=task.s_id
            )
            RedisEx().hmset(key, task.to_dict())
            TaskHelper().edit(task)
            RedisEx().push(
                '{}:crawler:{}'.format(self.task_config.in_queue_topic, task.s_priority.lower()),
                '{}:{}:{}'.format(self.task_config.record_key, task.s_platform, task.s_id)
            )
            log.debug('Push Main Task({}).'.format(task.s_feature))

    def _task_recycle(self):
        for event in RedisEx().psubscribe('__keyevent@0__:expired'):
            if event.get('type') == 'psubscribe' \
                or event.get('data') == 1 \
                    or (self.task_config.record_key + ':') not in event.get('data'):
                continue
            log.info(event)
            task_index = event.get('data')
            task_index = ':'.join(task_index.split(':')[:-1])
            task = RedisEx().get_records(task_index)
            if not task:
                continue
            task = TimingTask(**task)
            if self.task_filter(task):
                continue
            task.i_state = TimingTaskStatus.CrawlTopic
            RedisEx().push(
                '{}:crawler{}'.format(
                    self.task_config.in_queue_topic,
                    ':{}'.format(task.s_priority) if task.s_priority else ''
                ),
                '{}:{}:{}'.format(self.task_config.record_key, task.s_platform, task.s_id)
            )

    def task_interrupt_changed(self, task_info):
        features = RedisEx().hget('tddc:task:filter', task_info.s_platform)
        features = set(features.split(',')) if features else set()
        if task_info.b_interrupt:
            if task_info.s_feature in features:
                return
            features.add(task_info.s_feature)
        else:
            if task_info.s_feature not in features:
                return
            features.remove(task_info.s_feature)
        if features:
            RedisEx().hset('tddc:task:filter', task_info.s_platform, ','.join(features))
        else:
            RedisEx().hdel('tddc:task:filter', task_info.s_platform)
        event_id = ShortUUID.UUID()
        data = {'e_type': EVENT_All_TASK_FILTER_UPDATE,
                'name': 'Task Interrupt Changed',
                'describe': 'Task ({}) Interrupt Changed.'.format(task_info.s_platform),
                'event': task_info.to_dict(),
                'id': event_id,
                'status': 0,
                'timestamp': int(time.time())}
        RedisEx().publish(
            '{}:crawler'.format(self.event_config.topic), json.dumps(data)
        )
        RedisEx().publish(
            '{}:parser'.format(self.event_config.topic), json.dumps(data)
        )
        self.task_filter_update()


@six.add_metaclass(Singleton)
class TaskPadHelper(object):

    key_base = 'tddc:task:config:keep'

    def __init__(self):
        log.info('Task Pad Helper Starting.')
        super(TaskPadHelper, self).__init__()
        self.event_config = type('EventConfig', (), OnlineConfig().event.default)
        gevent.spawn(self._run_task_pad)
        gevent.sleep()
        log.info('Task Pad Helper Was Ready.')

    def edit(self, task):
        RedisEx().hmset(
            '{}:{}:{}'.format(self.key_base, task.s_owner.lower(), task.s_feature),
            task.to_dict()
        )

    def delete(self, platform, feature):
        RedisEx().delete(
            '{}:{}:{}'.format(self.key_base, platform.lower(), feature)
        )

    def query(self, platform='*', feature='*'):
        platform = platform.lower()
        if platform == '*':
            keys = RedisEx().keys('{}:*'.format(self.key_base))
            return [KeepTask(**RedisEx().hgetall(key)) for key in keys]
        else:
            if feature == '*':
                keys = RedisEx().keys('{}:{}:*'.format(self.key_base, platform))
                return [KeepTask(**RedisEx().hgetall(key)) for key in keys]
            else:
                key = RedisEx().keys('{}:{}:{}'.format(
                    self.key_base, platform, feature)
                )
                if key:
                    key = key[0]
                    return KeepTask(**RedisEx().hgetall(key))
                return None

    def start_task(self, task):
        if not self._assign_task_to_head(task):
            log.warning('Assign Task({}:{}) Failed.'.format(
                task.s_owner, task.s_feature
            ))
            return
        task.b_valid = True
        task.i_state = KeepTaskStatus.Dispatched
        self.edit(task)
        event = Event(KeepTaskEvent)
        event.data = task.to_dict()
        RedisEx().publish(
            '{}:{}'.format(self.event_config.topic, task.s_owner.lower()),
            json.dumps(event.to_dict())
        )
        log.debug('Task Pad Task({}:{}) Dispatched.'.format(
            task.s_owner, task.s_feature
        ))

    def stop_task(self, task):
        task.b_valid = False
        task.i_state = KeepTaskStatus.Stop
        self.edit(task)
        event = Event(KeepTaskEvent)
        event.data = task.to_dict()
        RedisEx().publish(
            '{}:{}'.format(self.event_config.topic, task.s_owner.lower()),
            json.dumps(event.to_dict())
        )

    @staticmethod
    def _get_heads(owner):
        keys = RedisEx().keys('tddc:worker:monitor:health:*')
        for key in keys:
            if key.split(':')[-1] == owner.lower():
                return RedisEx().hgetall(key)
        return None

    def _get_the_most_suitable_head(self, owner):
        heads = self._get_heads(owner)
        if not heads:
            return None
        ts = time.time()
        heads = {k: v for k, v in heads.items() if ts - float(v) < 30}
        the_most_suitable_head = None
        the_most_suitable_head_score = 100
        for head, heart in heads.items():
            mac, feature = head.split('|')
            name = 'tddc:worker:monitor:memory_usage_rate:{}'.format(mac)
            hkeys = RedisEx().hkeys(name)
            if hkeys:
                hkeys.sort()
                hkeys = hkeys[-5:]
                mem_percent_avg = sum(
                    [json.loads(RedisEx().hget(name, k)).get('mem_percent') for k in hkeys]
                ) / len(hkeys)
            else:
                mem_percent_avg = 0
            name = 'tddc:worker:monitor:cpu_usage_rate:{}'.format(mac)
            hkeys = RedisEx().hkeys(name)
            if hkeys:
                hkeys.sort()
                hkeys = hkeys[-5:]
                cpu_count = json.loads(RedisEx().hget(name, hkeys[0])).get('cpu_count')
                cpu_percent_avg = sum(
                    [sum(json.loads(RedisEx().hget(name, k)).get('cpu_percent')) / cpu_count for k in hkeys]
                ) / len(hkeys)
            else:
                cpu_percent_avg = 0
            score = mem_percent_avg * 0.4 + cpu_percent_avg * 0.6
            if score < the_most_suitable_head_score:
                the_most_suitable_head = head
                the_most_suitable_head_score = score
            elif score == the_most_suitable_head_score:
                the_most_suitable_head = random.choice([the_most_suitable_head, head])
                the_most_suitable_head_score = score
        return the_most_suitable_head

    def _assign_task_to_head(self, task):
        head = self._get_the_most_suitable_head(task.s_owner)
        if not head:
            return False
        task.head.set_head(head)
        task.state.set_state(KeepTaskStatus.Dispatched)
        return True

    def _run_task_pad(self):
        while True:
            try:
                ts = time.time()
                keys = RedisEx().keys('{}:*'.format(self.key_base))
                dispatch = []
                for key in keys:
                    task = KeepTask(**RedisEx().hgetall(key))
                    if not task.b_valid:
                        continue
                    if task.i_state == KeepTaskStatus.Dispatched:
                        if ts - task.i_timestamp <= 60:
                            continue
                    elif task.i_state == KeepTaskStatus.Running:
                        if ts - task.i_timestamp <= 60:
                            continue
                    elif task.i_state == KeepTaskStatus.Reconnect:
                        if ts - task.i_timestamp <= 300:
                            continue
                    elif task.i_state == KeepTaskStatus.Stop:
                        if ts - task.i_timestamp <= 300:
                            continue
                    else:
                        continue
                    if task.s_owner and task.s_id and task.s_feature:
                        dispatch.append(task)
                        task.state.set_state(KeepTaskStatus.Dispatched)
                for task in dispatch:
                    event = Event(KeepTaskEvent)
                    event.data = task.to_dict()
                    if not self._assign_task_to_head(task):
                        log.warning('Assign Task({}:{}) Failed.'.format(
                            task.s_owner, task.s_feature
                        ))
                        continue
                    RedisEx().publish(
                        '{}:{}'.format(self.event_config.topic, task.s_owner.lower()),
                        json.dumps(event.to_dict())
                    )
                    log.debug('Task Pad Task({}:{}) Dispatched.'.format(
                        task.s_owner, task.s_feature
                    ))
            except Exception as e:
                log.exception(e)
            gevent.sleep(15)
