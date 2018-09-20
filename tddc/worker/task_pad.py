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

from ..util.json_object_serialization import JsonObjectSerialization
from ..util.snowflake import SnowFlakeID
from ..util import Singleton
from ..config import default_config

from .event import EventCenter, Event
from .redisex import RedisEx

log = logging.getLogger(__name__)


class TaskPadEvent(JsonObjectSerialization):

    fields = ('id', 'timestamp', 'owner', 'valid', 'task_id')

    def __init__(self, fields=None, **kwargs):
        super(TaskPadEvent, self).__init__(fields, **kwargs)
        self.id = kwargs.get('id', SnowFlakeID().get_id())
        self.timestamp = kwargs.get('timestamp', int(time.time()))


class TaskPadTask(JsonObjectSerialization):

    class Status(object):
        Dispatched = 1
        Running = 2
        Stop = 3

    fields = ('id', 'timestamp', 'valid', 'owner', 'platform', 'feature', 'status', 'proxy')

    def __init__(self, fields=None, **kwargs):
        super(TaskPadTask, self).__init__(fields, **kwargs)
        self.id = kwargs.get('id', SnowFlakeID().get_id())
        self.timestamp = kwargs.get('timestamp', int(time.time()))


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
        name = 'tddc:task_pad:tasks:{}'.format(event.owner)
        task = RedisEx().hgetall(
            name, event.task_id
        )
        if not task:
            log.warning('Task Not Found.{}'.format(event))
            return
        if event.valid:
            self.start_task(task)
            RedisEx().set_record_item_value(
                name, event.task_id, TaskPadTask.Status.Running
            )
        else:
            self.stop_task(task)
            RedisEx().set_record_item_value(
                name, event.task_id, TaskPadTask.Status.Stop
            )

    def start_task(self, task):
        raise NotImplementedError

    def stop_task(self, task):
        raise NotImplementedError
