# encoding: utf-8
"""
@version: ??
@author: chenyitao
@license: Apache Licence 
@software: PyCharm
@file: event_model.py
@time: 2019-03-06 13:45
"""
import time

import logging

from ...base.util import JsonObjectSerialization, SnowFlakeID

from ..redisex import RedisEx

log = logging.getLogger(__name__)


class EventBase(JsonObjectSerialization):

    event = None

    name = ''

    desc = ''


class Event(JsonObjectSerialization):

    class Status(object):
        Pushed = 1001
        Fetched = 2001
        Executed_Success = 3200
        Executed_Failed = 3400

    fields = [
        's_id', 'i_timestamp', 'i_state', 'i_event', 's_name', 's_desc', 'd_data'
    ]

    def __init__(self, data_cls, **kwargs):
        super(Event, self).__init__(None, **kwargs)
        self.data_cls = data_cls
        self.s_id = kwargs.get('s_id', SnowFlakeID().get_id())
        self.i_timestamp = kwargs.get('i_timestamp', int(time.time()))
        self.i_event = kwargs.get('i_event', data_cls.event)
        self.i_name = kwargs.get('s_name', data_cls.name)
        self.i_desc = kwargs.get('s_desc', data_cls.desc)
        self.i_state = kwargs.get('i_state', Event.Status.Pushed)
        self.d_data = data_cls(**kwargs.get('d_data', {}))

    @property
    def _record_key(self):
        return 'tddc:event:record:{}'.format(self.data_cls.event)

    def set_attr_to_remote(self, name, value):
        key = '{}:{}'.format(
            self._record_key, self.s_id
        )
        RedisEx().hset(key, name, value)

    @property
    def data(self):
        return self.d_data

    @data.setter
    def data(self, new_data):
        if isinstance(new_data, self.data_cls):
            return
        elif isinstance(new_data, dict):
            self.d_data = self.data_cls(**new_data)
        else:
            raise Exception(
                'Parameter must be either a dictionary or {} types.'.format(self.data_cls)
            )

    def set_state(self, state):
        self.set_attr_to_remote('i_state', state)
        self.set_attr_to_remote('i_timestamp', int(time.time()))

    def to_dict(self):
        d = {k: self.__dict__.get(k)
             for k in self.fields
             if self.__dict__.get(k) is not None}
        d['d_data'] = self.data.to_dict()
        return d
