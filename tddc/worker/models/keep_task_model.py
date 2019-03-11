# -*- coding: utf-8 -*-
"""
@author  : chenyitao
@email   : yt.chen@bshier.com
@license: Apache Licence
@software: PyCharm
@file    : task_pad.py
@time    : 2018/9/18 14:00
"""
import hashlib
import time

import logging

from ...base.util import JsonObjectSerialization, SnowFlakeID
from ...worker.define.event import KeepTaskStateChange

from ..redisex import RedisEx
from ..event import Event

from .event_model import EventBase

log = logging.getLogger(__name__)


class _Task(JsonObjectSerialization):

    fields = [
        'i_timestamp'
    ]

    def __init__(self, fields=None, **kwargs):
        super(_Task, self).__init__(fields, **kwargs)
        self.i_timestamp = kwargs.get('i_timestamp', int(time.time()))

    @property
    def _record_key(self):
        return 'tddc:task:config:keep'

    def set_attr_to_remote(self, name, value):
        key = '{}:{}:{}'.format(
            self._record_key, self.s_owner.lower(), self.s_feature
        )
        RedisEx().hset(key, name, value)


class KeepTaskStatus(_Task):

    Dispatched = 1

    Running = 2

    Reconnect = 3

    Stop = 4

    fields = [
        's_id', 's_platform', 's_feature', 'i_state', 's_owner'
    ]

    def set_state(self, state):
        self.set_attr_to_remote('i_state', state)
        self.set_attr_to_remote('i_timestamp', int(time.time()))


class KeepTaskHead(_Task):

    fields = [
        's_id', 's_platform', 's_feature', 's_head', 's_owner'
    ]

    def set_head(self, head):
        self.set_attr_to_remote('s_head', head)


class KeepTask(_Task):

    fields = (
        's_id', 'i_timestamp', 'b_valid', 's_owner', 's_head',
        's_platform', 's_feature', 'i_state', 's_proxy'
    )

    def __init__(self, platform=None, feature=None, fields=None, **kwargs):
        super(KeepTask, self).__init__(fields, **kwargs)

        self.i_timestamp = kwargs.get('i_timestamp', int(time.time()))
        platform = platform or kwargs.get('s_platform')
        if platform:
            self.update_platform(platform)
        else:
            raise Exception('platform not found in args and s_platform not found in kwargs.')
        feature = feature or kwargs.get('s_feature')
        if feature:
            self.update_feature(feature)
        else:
            raise Exception('feature not found in args and s_feature not found in kwargs.')

    def update_platform(self, platform):
        self.s_platform = platform
        self.s_id = hashlib.md5(
            '{}{}'.format(self.s_platform, self.s_feature).encode()
        ).hexdigest()

    def update_feature(self, feature):
        self.s_feature = feature
        self.s_id = hashlib.md5(
            '{}{}'.format(self.s_platform, self.s_feature).encode()
        ).hexdigest()

    @property
    def state(self):
        return KeepTaskStatus(**self.to_dict())

    @property
    def head(self):
        return KeepTaskHead(**self.to_dict())


class KeepTaskEvent(EventBase):

    event = KeepTaskStateChange

    name = 'KeepTaskStateChange'

    desc = 'KeepTaskStateChange'

    fields = KeepTask.fields

    def __init__(self, task=None, **kwargs):
        if task:
            super(KeepTaskEvent, self).__init__(**task.to_dict())
        else:
            super(KeepTaskEvent, self).__init__(**kwargs)
