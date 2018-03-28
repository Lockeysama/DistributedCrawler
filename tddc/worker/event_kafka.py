# -*- coding: utf-8 -*-
'''
Created on 2017年5月5日

@author: chenyitao
'''
import logging
import gevent.queue

from ..kafka.consumer import KeepAliveConsumer
from ..util.util import Singleton

from .models import DBSession, KafkaModel, EventModel, WorkerModel
from .status import StatusManager
from .cache import CacheManager
from .record import RecordManager


class EventType(object):
    ExternModuleUpdate = 1001


class EventStatus(object):
    Pushed = 1001
    Fetched = 2001
    Executed_Success = 3200
    Executed_Failed = 3400


log = logging.getLogger(__name__)


class EventCenter(KeepAliveConsumer):
    '''
    classdocs
    '''
    __metaclass__ = Singleton

    _dispatcher = {}

    def __init__(self):
        StatusManager()
        CacheManager()
        RecordManager()
        self._event_queue = gevent.queue.Queue()
        self._event_call = {}
        self.worker = DBSession.query(WorkerModel).get(1)
        self.event_config = DBSession.query(EventModel).get(1)
        kafka_info = DBSession.query(KafkaModel).all()
        if not kafka_info:
            log.warning('>>> Kafka Nodes Not Found.')
            return
        kafka_nodes = ','.join(['%s:%s' % (info.host, info.port) for info in kafka_info])
        super(EventCenter, self).__init__(self.event_config.topic,
                                          self.event_config.group_id,
                                          0xffffffff,
                                          bootstrap_servers=kafka_nodes)
        log.info('Event Manager Is Starting.')
        self._event_call = {}
        log.info('Event Manager Was Ready.')

    @classmethod
    def route(cls, event_type):
        def decorator(func):
            EventCenter._dispatcher[event_type] = func
            return func
        return decorator

    def _record_fetched(self, item):
        event = item
        if not hasattr(event, 'id'):
            return
        self.update_the_status(event, EventStatus.Fetched)
        callback = self._dispatcher.get(event.e_type, None)
        if callback:
            callback(event)

    def _deserialization(self, item):
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
