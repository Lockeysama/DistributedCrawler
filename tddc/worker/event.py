# -*- coding: utf-8 -*-
'''
Created on 2017年5月5日

@author: chenyitao
'''
import json
import logging

import gevent.queue

from tddc import ShortUUID, time
from ..util.util import Singleton

from .models import DBSession, WorkerModel, EventModel
from .pubsub import Pubsub
from .status import StatusManager
from .cache import CacheManager
from .record import RecordManager

log = logging.getLogger(__name__)


class Event(object):
    class Type(object):
        ExternModuleUpdate = 1001

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


class EventCenter(Pubsub):
    '''
    事件中心
    '''
    __metaclass__ = Singleton

    _dispatcher = {}

    def __init__(self):
        log.info('Event Manager Is Starting.')
        StatusManager()
        CacheManager()
        RecordManager()
        self._event_queue = gevent.queue.Queue()
        self._event_call = {}
        self.worker = DBSession.query(WorkerModel).get(1)
        self.event_config = DBSession.query(EventModel).get(1)
        super(EventCenter, self).__init__()
        self._event_call = {}
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
        StatusManager().set_the_hash_value_for_the_hash('tddc:event:status:' + event.event.get('platform'),
                                                        event.id,
                                                        'tddc:event:status:value:' + event.id,
                                                        '%s|%s' % (self.worker.name, self.worker.id),
                                                        status)
        StatusManager().sadd('tddc:event:status:processing:%s' % event.event.get('platform'),
                             event.id)
