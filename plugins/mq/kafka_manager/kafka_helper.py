# -*- coding: utf-8 -*-
'''
Created on 2017年5月2日

@author: chenyitao
'''
from kafka import KafkaConsumer
from kafka.producer.kafka import KafkaProducer


class KafkaHelper(object):
    '''
    classdocs
    '''

    @classmethod
    def make_consumer(cls, bootstrap_servers=None, topic=None, group=None, enable_auto_commit=True):
        if not bootstrap_servers:
            bootstrap_servers = 'localhost:9092'
        return KafkaConsumer(topic,
                             bootstrap_servers=bootstrap_servers,
                             group_id=group,
                             enable_auto_commit=enable_auto_commit,
                             heartbeat_interval_ms=9000,
                             consumer_timeout_ms=5000,
                             max_poll_records=32,
                             api_version=(0, 10, 1))

    @classmethod
    def make_producer(cls, bootstrap_servers=None):
        if not bootstrap_servers:
            bootstrap_servers = 'localhost:9090'
        return KafkaProducer(bootstrap_servers=bootstrap_servers,
                             api_version=(0, 10, 1))

