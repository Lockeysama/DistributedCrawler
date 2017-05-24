# -*- coding: utf-8 -*-
'''
Created on 2017年5月5日

@author: chenyitao
'''

import gevent.queue
import json

from common import TDDCLogging

from plugins import KafkaHelper
from common.models.events import *
from StdSuites.AppleScript_Suite import event


class EventManagreBase(object):
    '''
    classdocs
    '''
    
    NODES = None
    
    TOPIC = None
    
    GROUP = None

    def __init__(self):
        '''
        Constructor
        '''
        TDDCLogging.info('-->Event Manager Is Starting.')
        self._init_event()
        self._event_consumer = KafkaHelper.make_consumer(self.NODES,
                                                         self.TOPIC,
                                                         self.GROUP)
        self._event_queue = gevent.queue.Queue()
        self._event_call = {}
        gevent.spawn(self._recv)
        gevent.sleep()
        gevent.spawn(self._dispatch)
        gevent.sleep()
        TDDCLogging.info('-->Event Manager Was Ready.')

    def _init_event(self):
        self._events_cls = {EventType.Crawler.BASE_DATA: CrawlerBaseDataEvent,
                            EventType.Crawler.COOKIES: CrawlerCookiesEvent,
                            EventType.Crawler.MODULE: CrawlerModuleEvent,
                            EventType.Parser.BASE_DATA: ParserBaseDataEvent,
                            EventType.Parser.MODULE: ParseModuleEvent,
                            EventType.ProxyChecker.BASE_DATA: ProxyCheckerBaseDataEvent,
                            EventType.ProxyChecker.MODULE: ProxyCheckerModuleEvent,
                            EventType.ProxyChecker.SOURCE: ProxyCheckerSourceAPIEvent,
                            EventType.CookiesGenerator.BASE_DATA: CookiesGeneratorBaseDataEvent,
                            EventType.CookiesGenerator.MODULE: CookiesGeneratorModuleEvent,
                            EventType.Monitor.BASE_DATA: MonitorBaseDataEvent,
                            EventType.Monitor.MODULE: MonitorExceptionProcessModuleEvent}

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
