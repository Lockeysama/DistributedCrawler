# -*- coding: utf-8 -*-
'''
Created on 2017年5月5日

@author: chenyitao
'''

import json

import gevent.queue
from tddc.common import TDDCLogging
from tddc.common import singleton

from ..plugins import KafkaHelper


class EventType(object):

    PACKAGES_UPDATE = 1


@singleton
class EventCenter(object):
    '''
    classdocs
    '''

    def start(self, nodes, topic, group, event_cls):
        self._nodes = nodes
        self._topic = topic
        self._group = group
        self._events_cls = event_cls
        TDDCLogging.info('-->Event Manager Is Starting.')
        self._event_consumer = KafkaHelper.make_consumer(self._nodes,
                                                         self._topic,
                                                         self._group)
        self._event_queue = gevent.queue.Queue()
        self._event_call = {}
        gevent.spawn(self._recv)
        gevent.sleep()
        gevent.spawn(self._dispatch)
        gevent.sleep()
        TDDCLogging.info('-->Event Manager Was Ready.')

    def register(self, event_type, callback):
        self._event_call[event_type] = callback

    def _recv(self):
        while True:
            for record in self._event_consumer:
                self._event_parse(record)
            gevent.sleep(5)
    
    def _event_parse(self, record):
        try:
            item = json.loads(record.value)
        except Exception, e:
            self._consume_msg_exp('EVENT_JSON_ERR', record.value, e)
        else:
            if item and isinstance(item, dict):
                event_type = item.get('event_type')
                if not event_type:
                    self._consume_msg_exp('EVENT_ERR', item)
                    return
                cls = self._events_cls.get(event_type)
                if not cls:
                    TDDCLogging.error('Undefine Event Type: %d <%s>' % (event_type,
                                                                        json.dumps(item)))
                    return
                event = cls(**item)
                self._event_queue.put(event)
            else:
                self._consume_msg_exp('EVENT_ERR', item)

    def _dispatch(self):
        while True:
            event = self._event_queue.get()
            callback = self._event_call.get(event.event_type, None)
            if callback:
                callback(event)
            else:
                TDDCLogging.warning('Event Exception: %d Not Register.' % event.event_type)

    def _consume_msg_exp(self, exp_type, info, exception=None):
        if 'JSON_ERR' in exp_type:
            TDDCLogging.error('*'*5+exp_type+'*'*5+
                              '\nException: '+info+'\n'+
                              exception.message+'\n'+
                              '*'*(10+len(exp_type))+'\n')
        elif 'TASK_ERR' in exp_type or 'EVENT_ERR' in exp_type:
            TDDCLogging.error('*'*5+exp_type+'*'*5+
                              '\nException: '+
                              'item={item}\n'.format(item=info)+
                              'item_type={item_type}\n'.format(item_type=type(info))+
                              '*'*(10+len(exp_type))+'\n')
                
