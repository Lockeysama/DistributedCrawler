# -*- coding: utf-8 -*-
"""
Created on 2017年5月5日

@author: chenyitao
"""
import json
import logging
import time

import gevent.queue

from ..base.util import ShortUUID, Singleton
from ..default_config import default_config

from redisex import RedisEx

log = logging.getLogger(__name__)


class Event(object):
    class Type(object):
        ExtraModuleUpdate = 1001
        TaskFilterUpdate = 2001
        LogOnlineSwitch = 3001
        OnlineConfigFlush = 4001
        LongTaskStatusChange = 5001

    class Status(object):
        Pushed = 1001
        Fetched = 2001
        Executed_Success = 3200
        Executed_Failed = 3400

    id = None

    own = None

    platform = None

    feature = None

    url = None

    file_md5 = None

    package = None

    mould = None

    version = None

    valid = None

    status = None

    timestamp = None

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            self.__dict__[k] = v
        self.id = kwargs.get('id', ShortUUID.UUID())
        self.timestamp = kwargs.get('timestamp', int(time.time()))

    def to_dict(self):
        return self.__dict__


class EventCenter(RedisEx):
    """
    事件中心
    """
    __metaclass__ = Singleton

    _dispatcher = {}

    def __init__(self):
        log.info('Event Manager Is Starting.')
        self._event_queue = gevent.queue.Queue()
        self._event_call = {}
        from online_config import OnlineConfig
        self.event_config = OnlineConfig().event
        super(EventCenter, self).__init__()
        self._event_call = {}
        gevent.spawn_later(3, self.subscribing)
        gevent.sleep()
        log.info('Event Manager Was Ready.')

    @classmethod
    def route(cls, event_type):
        """
        绑定事件与回调函数
        :param event_type:
        :return:
        """
        def decorator(func):
            EventCenter._dispatcher[event_type] = func
            return func
        return decorator

    def _subscribe_topic(self):
        return self.event_config.topic

    def _data_fetched(self, data):
        event = self._deserialization(data)
        if not event or not hasattr(event, 'id'):
            return
        self.update_the_status(event, Event.Status.Fetched)
        callback = self._dispatcher.get(event.e_type, None)
        if callback:
            callback(event)

    def _deserialization(self, data):
        """
        转化event
        :param data:
        :return:
        """
        try:
            item = json.loads(data)
        except Exception as e:
            log.warning('Event:"%s" | %s.' % (data, e.message))
            return None
        if not isinstance(item, dict):
            log.warning('Event:"%s" is not type of dict.' % data)
            return None
        return type('EventRecord', (), item)

    def update_the_status(self, event, status):
        """
        :param event: Event Detail Info
        :param status: Event Executive Condition
        :return:
        Status Structure(Redis):
            name(table type: hash)
            key(event id)
            value(key from hash(name('xxx:xx:x:event_id')))
        """
        RedisEx().set_the_hash_value_for_the_hash(
            'tddc:event:status:{}'.format(event.event.get('platform')),
            str(event.id),
            'tddc:event:status:value:{}'.format(event.id),
            '{}|{}'.format(default_config.PLATFORM, default_config.FEATURE),
            status
        )
        RedisEx().sadd(
            'tddc:event:status:processing:%s' % event.event.get('platform'),
            event.id
        )
