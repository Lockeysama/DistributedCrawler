# -*- coding: utf-8 -*-
'''
Created on 2017年4月7日

@author: chenyitao
'''

import json
import gevent
from pykafka import KafkaClient

from common.queues import EXCEPTION_QUEUE, EVENT_QUEUE
from conf.base_site import KAFKA_HOST, KAFKA_PORT, ZK_HOST_PORTS, STATUS,\
    EXCEPTION_TOPIC_NAME
from plugins.mq.kafka_manager.consumer import Consumer
from plugins.mq.kafka_manager.producer import Producer
import pykafka
import kazoo
import logging
from worker.parser.models.event import Event


class TaskManagerBase(object):
    '''
    classdocs
    '''

    event_topic_name = ''
    
    event_topic_group = ''

    def __init__(self, callback=None):
        '''
        Constructor
        '''
        print('-->MQ Manager Is Starting.')
        self._callback = callback
        self._cur_tag_num = 0
        self._exception_tag = 1000
        self._event_tag = 2000
        self._tag_num = self._exception_tag + self._event_tag
        self._init_kafka_log()
        self._client = KafkaClient(hosts='{host}:{port}'.format(host=KAFKA_HOST,
                                                                port=KAFKA_PORT))
        self._exception_task_producer = self.make_producer(EXCEPTION_TOPIC_NAME)
        gevent.spawn(self._push_exception_task)
        gevent.sleep()
        self._event_consumer = self.make_consumer(self.event_topic_name,
                                                  self.event_topic_group,
                                                  True)
        gevent.spawn(self._fetch_event)
        gevent.sleep()

    def _init_kafka_log(self):
        log = logging.getLogger('kafka')
        log.setLevel(logging.WARNING)
        pykafka.simpleconsumer.log = log
        pykafka.balancedconsumer.log = log
        pykafka.producer.log = log
        pykafka.cluster.log = log
        pykafka.handlers.log = log
        pykafka.connection.log = log
        kazoo.client.log = log

    def _ready(self, tag):
        self._cur_tag_num += tag
        if self._cur_tag_num == self._tag_num:
            print('-->MQ Manager Was Ready.')
            if self._callback:
                self._callback()

    def _consume_msg_exp(self, exp_type, info, exception=None):
        if 'JSON_ERR' in exp_type:
            print('*'*5+exp_type+'*'*5+
                  '\nException: '+info+'\n'+
                  exception.message+'\n'+
                  '*'*(10+len(exp_type))+'\n')
        elif 'TASK_ERR' in exp_type or 'EVENT_ERR' in exp_type:
            print('*'*5+exp_type+'*'*5+
                  '\nException: '+
                  'item={item}\n'.format(item=info)+
                  'item_type={item_type}\n'.format(item_type=type(info))+
                  '*'*(10+len(exp_type))+'\n')

    def make_consumer(self, topic, group, auto_commit=False):
        consumer = Consumer(kafka_client=self._client,
                            topic=topic,
                            zk=','.join(ZK_HOST_PORTS),
                            group=group,
                            auto_commit=auto_commit)
        return consumer
    
    def make_producer(self, topic):
        producer = Producer(kafka_client=self._client,
                            topic=topic)
        return producer
    
    def _fetch_event(self):
        print('--->Event Consumer Was Ready.')
        self._ready(self._event_tag)
        while STATUS:
            msgs = self._event_consumer.start()
            for msg in msgs:
                try:
                    item = json.loads(msg.value)
                except Exception, e:
                    self._consume_msg_exp('EVENT_JSON_ERR', msg.value, e)
                else:
                    if item and isinstance(item, dict) and item.get('type', None):
                        event = Event(item)
                        EVENT_QUEUE.put(event)
                    else:
                        self._consume_msg_exp('EVENT_ERR', item) 
 
    def _push_exception_task(self):
        print('--->Exception Producer Was Ready.')
        self._ready(self._exception_tag)
        while STATUS:
            task = EXCEPTION_QUEUE.get()
            msg = json.dumps(task.__dict__)
            if msg:
                self._exception_task_producer.push(msg)

    
    def __del__(self):
        print('del', self.__class__)
