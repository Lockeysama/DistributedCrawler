# -*- coding: utf-8 -*-
"""
Created on 2017年5月5日

@author: chenyitao
"""
import json
import logging

import gevent.queue
import six

from ..base.util import Singleton

from .redisex import RedisEx
from .models.event_model import Event

log = logging.getLogger(__name__)


@six.add_metaclass(Singleton)
class EventCenter(RedisEx):
    """
    事件中心
    """

    _dispatcher = {}

    def __init__(self):
        log.info('Event Manager Is Starting.')
        self._event_queue = gevent.queue.Queue()
        self._event_call = {}
        from .online_config import OnlineConfig
        self.event_config = type('EventConfig', (), OnlineConfig().event.default)
        super(EventCenter, self).__init__()
        self._event_call = {}
        gevent.spawn_later(3, self.subscribing)
        gevent.sleep()
        log.info('Event Manager Was Ready.')

    @classmethod
    def route(cls, event_cls):
        """
        绑定事件与回调函数
        :param event_cls:
        :return:
        """
        def decorator(func):
            EventCenter._dispatcher[event_cls.event] = (func, event_cls)
            return func
        return decorator

    def _subscribe_topic(self):
        return self.event_config.topic

    def _data_fetched(self, data):
        event = self._deserialization(data)
        if not event or not event.get('s_id'):
            return
        callback, event_cls = self._dispatcher.get(event.get('i_event'), None)
        if callback:
            event = Event(event_cls, **event)
            callback(event)
            event.set_state(Event.Status.Fetched)

    def _deserialization(self, data):
        """
        转化event
        :param data:
        :return:
        """
        try:
            item = json.loads(data)
        except Exception as e:
            log.warning('Event:"%s" | %s.' % (data, e.args[0]))
            return None
        if not isinstance(item, dict):
            log.warning('Event:"%s" is not type of dict.' % data)
            return None
        return item
