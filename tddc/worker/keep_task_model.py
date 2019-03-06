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

from ..base.util import JsonObjectSerialization, SnowFlakeID

from .redisex import RedisEx
from .event import Event

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


class KeepTaskEvent(JsonObjectSerialization):

    fields = ('s_id', 'i_timestamp', 'i_event', 'i_state'
              's_owner', 's_head', 'd_data')

    def __init__(self, fields=None, **kwargs):
        super(KeepTaskEvent, self).__init__(fields, **kwargs)
        self.s_id = kwargs.get('s_id', SnowFlakeID().get_id())
        self.i_timestamp = kwargs.get('i_timestamp', int(time.time()))
        self.i_event = kwargs.get('i_event', Event.Type.LongTaskStatusChange)
        self.i_state = kwargs.get('i_state', Event.Status.Pushed)
        self.d_data = KeepTask(**kwargs.get('d_data')) if kwargs.get('d_data') else None

    @property
    def data(self):
        return self.d_data

    @data.setter
    def data(self, new_data):
        self.d_data = KeepTask(**new_data)

    def to_dict(self):
        d = {k: self.__dict__.get(k)
             for k in self.fields
             if self.__dict__.get(k) is not None}
        d['d_data'] = self.data.to_dict()
        return d
