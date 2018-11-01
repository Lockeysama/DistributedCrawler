# -*- coding: utf-8 -*-
"""
@author  : chenyitao
@email   : yt.chen@bshier.com
@license: Apache Licence
@software: PyCharm
@file    : task_pad.py
@time    : 2018/9/18 14:00
"""
import time
from os import getpid

import logging

from ..base.util import JsonObjectSerialization, SnowFlakeID, Singleton
from ..default_config import default_config

from event import EventCenter, Event
from redisex import RedisEx

log = logging.getLogger(__name__)


class TaskPadEvent(JsonObjectSerialization):

    fields = ('s_id', 'i_timestamp', 's_owner', 's_head', 'b_valid', 's_task_id')

    def __init__(self, fields=None, **kwargs):
        super(TaskPadEvent, self).__init__(fields, **kwargs)
        self.s_id = kwargs.get('s_id', SnowFlakeID().get_id())
        self.i_timestamp = kwargs.get('i_timestamp', int(time.time()))


class TaskPadTask(JsonObjectSerialization):

    class Status(object):
        Dispatched = 1
        Running = 2
        Reconnect = 3
        Stop = 4

    fields = (
        's_id', 'i_timestamp', 'b_valid', 's_owner', 's_head',
        's_platform', 's_feature', 'i_status', 's_proxy'
    )

    def __init__(self, fields=None, **kwargs):
        super(TaskPadTask, self).__init__(fields, **kwargs)
        self.s_id = kwargs.get('s_id', SnowFlakeID().get_id())
        self.i_timestamp = kwargs.get('i_timestamp', int(time.time()))


class TaskPadManager(object):

    __metaclass__ = Singleton

    def __init__(self):
        super(TaskPadManager, self).__init__()

    @staticmethod
    @EventCenter.route(Event.Type.LongTaskStatusChange)
    def _task_status_change(event):
        if getpid() != default_config.PID:
            return
        log.info('Long Task Status Changed...')
        event_model = TaskPadEvent(**event.event)
        TaskPadManager().task_status_change(event_model)

    def task_status_change(self, event):
        name = 'tddc:task_pad:config:{}'.format(event.s_owner)
        task = RedisEx().hgetall(
            name, event.s_task_id
        )
        if not task:
            log.warning('Task Not Found.{}'.format(event))
            return
        if event.valid:
            self.start_task(task)
            RedisEx().set_record_item_value(
                name, event.s_task_id, TaskPadTask.Status.Running
            )
        else:
            self.stop_task(task)
            RedisEx().set_record_item_value(
                name, event.s_task_id, TaskPadTask.Status.Stop
            )

    def start_task(self, task):
        raise NotImplementedError

    def stop_task(self, task):
        raise NotImplementedError
