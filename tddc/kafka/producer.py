# -*- coding: utf-8 -*-
'''
Created on 2017年5月2日

@author: chenyitao
'''

import gevent.queue
import time
from kafka import KafkaProducer

from ..log.logger import TDDCLogger


class KeepAliveProducer(KafkaProducer, TDDCLogger):

    def __init__(self, bootstrap_servers):
        self.status = type('KafkaStatus', (), {'alive_timestamp': 0})
        super(KeepAliveProducer, self).__init__(bootstrap_servers=bootstrap_servers)
        self._queue = gevent.queue.Queue()
        gevent.spawn(self._push)
        gevent.sleep()
        gevent.spawn(self.alive_check)
        gevent.sleep()

    def alive_check(self):
        while True:
            try:
                self.send('ping', 'pong')
            except Exception as e:
                self.exception(e)
                self._sender.wakeup()
            else:
                self.status.alive_timestamp = int(time.time())
            gevent.sleep(5)

    def get_connection_status(self):
        return self.status

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
