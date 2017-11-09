# -*- coding: utf-8 -*-
'''
Created on 2017年5月5日

@author: chenyitao
'''

from string import capitalize

import gevent.queue

from ..log.logger import TDDCLogger
from ..config.config_center import ConfigCenter
from ..kafka.consumer import KeepAliveConsumer
from ..redis.status import StatusManager
from ..util.util import Singleton


class EventCenter(TDDCLogger):
    '''
    classdocs
    '''
    __metaclass__ = Singleton

    def __init__(self):
        super(EventCenter, self).__init__()
        self.info('Event Manager Is Starting.')
        self._event_queue = gevent.queue.Queue()
        self._event_call = {}
        event_info = ConfigCenter().get_event()
        kafka_info = ConfigCenter().get_services('kafka')
        if not kafka_info:
            self.error('Kafka Server Info Not Found.')
            return
        kafka_nodes = ','.join(['%s:%s' % (info.host, info.port) for info in kafka_info['kafka']])
        self._event_consumer = KeepAliveConsumer(event_info.topic,
                                                 event_info.group_id,
                                                 0xffffffff,
                                                 bootstrap_servers=kafka_nodes)
        self._event_call = {}
        gevent.spawn(self._recv)
        gevent.sleep()
        gevent.spawn(self._dispatch)
        gevent.sleep()
        self.info('Event Manager Was Ready.')

    def register(self, event_type, callback):
        self._event_call[event_type] = callback

    def _recv(self):
        while True:
            event = self._event_consumer.get()
            self._event_parse(event)
            gevent.sleep(5)

    def _event_parse(self, event):
        if not isinstance(event, dict):
            self.warning('Event Can\'t Parser.')
            return
        event = type(str(capitalize(event.get('name', 'OtherEvent'))),
                     (),
                     event)
        self._event_queue.put(event)

    def _dispatch(self):
        while True:
            event = self._event_queue.get()
            callback = self._event_call.get(event.event_type, None)
            if callback:
               callback(event)
            else:
                self.logger.warning('Event Exception: %d Not Found.' % event.event_type)
            self.update_status(event, 200, 1)

    def update_status(self, event, new_status, old_status):
        StatusManager().update_status('tddc.event.status.%d.' % event.event_type,
                                      event.id,
                                      new_status,
                                      old_status)
