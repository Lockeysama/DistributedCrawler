# -*- coding: utf-8 -*-
'''
Created on 2017年4月7日

@author: chenyitao
'''

import json
import gevent
from pykafka import KafkaClient

from common.queues import EXCEPTION_QUEUE
from conf.base_site import KAFKA_HOST, KAFKA_PORT, ZK_HOST_PORTS, STATUS,\
    EXCEPTION_TOPIC_NAME
from plugins.mq.kafka_manager.consumer import Consumer
from plugins.mq.kafka_manager.producer import Producer
import pykafka
import kazoo
import logging


class TaskManagerBase(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self._init_kafka_log()
        self._client = KafkaClient(hosts='{host}:{port}'.format(host=KAFKA_HOST,
                                                                port=KAFKA_PORT))
        self._exception_task_producer = self.make_producer(EXCEPTION_TOPIC_NAME)
        gevent.spawn(self._push_exception_task)
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
    
    def _push_exception_task(self):
        print('--->Exception Producer Was Ready.')
        while STATUS:
            task = EXCEPTION_QUEUE.get()
            msg = json.dumps(task.__dict__)
            if msg:
                self._exception_task_producer.push(msg)

    
    def __del__(self):
        print('del', self.__class__)
