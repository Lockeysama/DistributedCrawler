# -*- coding: utf-8 -*-
'''
Created on 2017年5月2日

@author: chenyitao
'''

import gevent.queue
from kafka import KafkaProducer

from ..config.config_center import ConfigCenter
from ..util.util import Singleton
from ..log.logger import TDDCLogger


class KeepAliveProducer(KafkaProducer, TDDCLogger):
    __metaclass__ = Singleton

    def __init__(self):
        kafka_info = ConfigCenter().get_services('kafka')
        if not kafka_info:
            self.error('Kafka Server Info Not Found.')
            return
        kafka_nodes = ','.join(['%s:%s' % (info.host, info.port) for info in kafka_info['kafka']])
        super(KeepAliveProducer, self).__init__(bootstrap_servers=kafka_nodes)
        self._queue = gevent.queue.Queue()
        gevent.spawn(self._push)
        gevent.sleep()

    def push(self, topic, data, callback):
        self._queue.put((topic, data, callback))

    def _push(self):
        while True:
            topic, data, callback = self._queue.get()
            try:
                self.send(topic, data)
            except Exception as e:
                self.exception(e)
            else:
                if callback:
                    callback(data)
