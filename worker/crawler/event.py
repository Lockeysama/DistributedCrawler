# -*- coding: utf-8 -*-
'''
Created on 2017年5月5日

@author: chenyitao
'''

import gevent.queue
import json

from conf.base_site import KAFKA_HOST_PORT
from conf.event_site import EVENT_TOPIC, EVENT_TOPIC_GROUP
from common import singleton, TDDCLogging
from common.models import Event

from plugins import KafkaHelper

class TDDCEvent(object):
    RULE_UPDATE = 0
    EXCEPTION_PROC_UPDATE = 1
    PLATFORM_CONFIG_UPDATE = 2
    

@singleton
class EventManagre(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        TDDCLogging.info('-->Event Manager Is Starting.')
        self._event_consumer = KafkaHelper.make_consumer(KAFKA_HOST_PORT,
                                                         EVENT_TOPIC,
                                                         EVENT_TOPIC_GROUP)
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
                try:
                    item = json.loads(record.value)
                except Exception, e:
                    self._consume_msg_exp('EVENT_JSON_ERR', record.value, e)
                else:
                    if item and isinstance(item, dict):
                        event = Event(**item)
                        self._event_queue.put(event)
                    else:
                        self._consume_msg_exp('EVENT_ERR', item)
            gevent.sleep(5)
    
    def _dispatch(self):
        while True:
            event = self._event_queue.get()
            callback = self._event_call.get(event.e_type, None)
            if callback:
                callback(event)
            else:
                print('Event Exception: %s Not Register.' % event.name)


def main():
    def rule_update(event):
        print('rule_update')
    
    def exception_proc_update(event):
        print('exception_proc_update')
    
    def platform_config_update(event):
        print('platform_config_update')
    
    EventManagre().register(TDDCEvent.RULE_UPDATE, rule_update)
    EventManagre().register(TDDCEvent.EXCEPTION_PROC_UPDATE, exception_proc_update)
    EventManagre().register(TDDCEvent.PLATFORM_CONFIG_UPDATE, platform_config_update)
    print(EventManagre()._event_call.items())
    
    gevent.sleep(10)
    p = KafkaHelper.make_producer()
    p.send(EVENT_TOPIC, json.dumps({'e_type': TDDCEvent.RULE_UPDATE,
                                    'name': 'event_test',
                                    'desc': 'no',
                                    'detail': {'platform': 'cheok'}}))

if __name__ == '__main__':
    import gevent.monkey
    gevent.monkey.patch_all(aggressive=False)
    main()
    gevent.sleep(1000)
