# -*- coding: utf-8 -*-
'''
Created on 2017年5月2日

@author: chenyitao
'''

import gevent.queue
from kafka import KafkaProducer

from ..log.logger import TDDCLogger


class KeepAliveProducer(KafkaProducer, TDDCLogger):

    def __init__(self, *args, **kwargs):
        super(KeepAliveProducer, self).__init__(*args, **kwargs)
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
            except Exception, e:
                self.logger.warning(e)
            else:
                if callback:
                    callback(topic, data)
