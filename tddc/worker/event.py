# -*- coding: utf-8 -*-
'''
Created on 2017年5月5日

@author: chenyitao
'''

from string import capitalize

import gevent.queue

from ..kafka.consumer import KeepAliveConsumer
from ..log.logger import TDDCLogger
from ..util.util import Singleton
from .status import StatusManager
from .worker_config import WorkerConfigCenter


class EventType(object):
    ExternModuleUpdate = 1001


class EventStatus(object):
    Pushed = 1001
    Fetched = 2001
    Executed_Success = 3200
    Executed_Failed = 3400


class EventCenter(KeepAliveConsumer):
    '''
    classdocs
    '''
    __metaclass__ = Singleton

    _dispatcher = {}

    def __init__(self):
        self._event_queue = gevent.queue.Queue()
        self._event_call = {}
        self.worker = WorkerConfigCenter().get_worker()
        event_info = WorkerConfigCenter().get_event()
        self.event_config = event_info
        kafka_info = WorkerConfigCenter().get_kafka()
        if not kafka_info:
            print('>>> Kafka Nodes Not Found.')
            return
        kafka_nodes = ','.join(['%s:%s' % (info.host, info.port) for info in kafka_info])
        super(EventCenter, self).__init__(event_info.topic,
                                          event_info.group_id,
                                          0xffffffff,
                                          bootstrap_servers=kafka_nodes)
        self.info('Event Manager Is Starting.')
        self._event_call = {}
        self.info('Event Manager Was Ready.')

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
        self.event_status_update(event, EventStatus.Fetched)
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
        StatusManager().set_the_hash_value_for_the_hash('tddc:event:status:' + event.platform,
                                                        event.id,
                                                        'tddc:event:status:value:' + event.id,
                                                        '%s_%s' % (self.worker.name, self.worker.id),
                                                        status)
        StatusManager().sadd('tddc:event:status:processing:%s' % event.platform)
