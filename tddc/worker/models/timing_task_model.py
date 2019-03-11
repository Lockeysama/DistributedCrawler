# encoding: utf-8
"""
@version: ??
@author: chenyitao
@license: Apache Licence 
@software: PyCharm
@file: task.py
@time: 2019-03-01 13:55
"""
import hashlib
import logging
import time

from ...base.util import JsonObjectSerialization
from ..online_config import OnlineConfig
from ..redisex import RedisEx
from ..define.event import TaskFilterUpdate

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
        return OnlineConfig().task.default.get('record_key')

    def set_attr_to_remote(self, name, value):
        key = '{}:{}:{}'.format(
            self._record_key, self.s_platform, self.s_id
        )
        RedisEx().hset(key, name, value)


class TimingTaskIndex(_Task):

    fields = [
        's_id', 's_platform'
    ]

    @classmethod
    def init_with_key(cls, key):
        s_platform, s_id = key.split(':')[-2:]
        data = {
            's_platform': s_platform, 's_id': s_id
        }
        return cls(**data)


class TimingTaskStatus(_Task):

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
        's_id', 's_platform', 's_feature', 'i_state'
    ]

    def set_state(self, state):
        self.set_attr_to_remote('i_state', state)


class _TimingTaskRecover(_Task):

    fields = [
        's_id', 's_platform', 's_feature', 'b_is_recover', 'i_state'
    ]

    def start(self):
        if self.b_is_recover:
            base = '{}:'.format(self._record_key)
            key = '{}:recover:countdown:{}:{}'.format(
                base, self.s_platform, self.s_id
            )
            RedisEx().setex(key, 300, self.i_state)

    def stop(self):
        if self.b_is_recover:
            base = '{}:'.format(self._record_key)
            key = '{}:recover:countdown:{}:{}'.format(
                base, self.s_platform, self.s_id
            )
            RedisEx().delete(key)


class _TimingTaskFilter(_Task):

    fields = [
        's_id', 's_platform', 's_feature', 'b_interrupt'
    ]

    def filter(self, filter_table):
        filter_features = filter_table.get(self.s_platform)
        if filter_features:
            if self.s_feature in filter_features:
                key = '{}:{}:{}'.format(
                    self._record_key, self.s_platform, self.s_id
                )
                RedisEx().delete(key)
                log.debug('[{}:{}:{}] Task Filter.'.format(
                    self.s_platform, self.s_feature, self.s_id
                ))
                return True
        return False


class _TimingTaskCache(_Task):

    fields = [
        's_id', 's_platform', 's_feature', 's_cache'
    ]

    def __init__(self, fields=None, **kwargs):
        super(_TimingTaskCache, self).__init__(fields, **kwargs)

    def set_cache(self):
        self.set_attr_to_remote('s_cache', self.s_cache)


class TimingTask(_Task):

    fields = [
        's_id',
        's_url', 's_platform', 's_feature',
        'i_state', 'i_timestamp',
        'i_space', 's_headers', 's_method', 's_proxy',
        's_data', 's_cookies', 's_params', 's_json',
        's_priority', 's_cache',
        'b_allow_redirects', 'b_interrupt', 'b_valid', 'b_is_recover',
        's_start_date', 's_timer', 's_desc'
    ]

    @classmethod
    def init_with_index(cls, index):
        key = '{}:{}:{}'.format(
            OnlineConfig().task.default.get('record_key'),
            index.s_platform, index.s_id
        )
        records = RedisEx().hgetall(key)
        return cls(**records)

    def __init__(self, url=None, fields=None, **kwargs):
        super(TimingTask, self).__init__(fields, **kwargs)
        self.s_method = kwargs.get('s_method', 'GET')
        self.s_proxy = kwargs.get('s_proxy', '')
        self.s_priority = kwargs.get('s_priority', 'middle')
        self.i_state = kwargs.get('i_state', TimingTaskStatus.CrawlTopic)
        self.b_allow_redirects = kwargs.get('b_allow_redirects', True)
        self.b_interrupt = kwargs.get('b_interrupt', False)
        self.b_is_recover = kwargs.get('b_is_recover', True)
        url = url or kwargs.get('s_url')
        if url:
            self.update_url(url)
        else:
            raise Exception('url not found in args and s_url not found in kwargs.')

    def update_url(self, url):
        self.s_url = url
        self.s_id = hashlib.md5(self.s_url.encode()).hexdigest()

    @property
    def index(self):
        return TimingTaskIndex(**self.to_dict())

    @property
    def state(self):
        return TimingTaskStatus(**self.to_dict())

    @property
    def cache(self):
        return _TimingTaskCache(**self.to_dict())

    @property
    def recover(self):
        return _TimingTaskRecover(**self.to_dict())

    @property
    def filter(self):
        return _TimingTaskFilter(**self.to_dict())

    def destroy(self):
        key = '{}:{}:{}'.format(
            self._record_key, self.s_platform, self.s_id
        )
        RedisEx().delete(key)


class TimingTaskFilterEvent(EventBase):

    event = TaskFilterUpdate

    name = 'TaskFilterUpdate'

    desc = 'TaskFilterUpdate'

    fields = TimingTask.fields

    def __init__(self, task=None, **kwargs):
        if task:
            super(TimingTaskFilterEvent, self).__init__(**task.to_dict())
        else:
            super(TimingTaskFilterEvent, self).__init__(**kwargs)
