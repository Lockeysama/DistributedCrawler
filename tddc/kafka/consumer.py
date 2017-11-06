# -*- coding: utf-8 -*-
'''
Created on 2017年5月2日

@author: chenyitao
'''

import json

import gevent.queue
from kafka import KafkaConsumer

from ..log.logger import TDDCLogger


class KeepAliveConsumer(KafkaConsumer, TDDCLogger):
    """
    Keep Alive Consumer
    """

    def __init__(self, topics, group, pause_size, record_model_cls=None, *args, **kwargs):
        self._topics = topics
        self._group = group
        self._pause_size = pause_size
        self._record_model_cls = record_model_cls
        super(KeepAliveConsumer, self).__init__(topics,
                                                group_id=group,
                                                api_version=(0, 10, 1),
                                                heartbeat_interval_ms=9000,
                                                consumer_timeout_ms=5000,
                                                max_poll_records=32,
                                                *args,
                                                **kwargs)
        self._queue = gevent.queue.Queue()
        gevent.spawn(self._fetch)
        gevent.sleep()

    def get(self, block=True, timeout=None):
        return self._queue.get(block, timeout)

    def _fetch(self):
        pause = False
        while True:
            if self._queue.qsize() > self._pause_size:
                if not pause:
                    self.commit()
                    self.unsubscribe()
                    pause = True
                    self.logger.info('Consumer[%s(%s)] Was Paused.' % (self._topics,
                                                                       self._group))
                gevent.sleep(1)
                continue
            if pause and self._queue.qsize() < self._pause_size / 2:
                self.subscribe(self._topics)
                pause = False
                self.logger.info('Consumer[%s(%s)] Was Resumed.' % (self._topics, self._group))
            partition_records = self.poll(2000, 16)
            if not len(partition_records):
                gevent.sleep(1)
                continue
            for _, records in partition_records.items():
                for record in records:
                    self._record(record)

    def _record(self, record):
        try:
            item = json.loads(record.value)
        except Exception, e:
            self.logger.error('\n' + '*' * 5 + 'JSON Error' + '*' * 5 +
                              '\nException: ' + record.value + '\n' +
                              e.message + '\n' +
                              '*' * (10 + len('JSON Error')) + '\n')
        else:
            if not item:
                return
            try:
                if self._record_model_cls:
                    item = self._record_model_cls(item)
            except Exception, e:
                self.logger.warning('Item(%s) is not type of %s' % (record.value,
                                                                    self._record_model_cls.__name__))
                self.logger.warning(e)
            else:
                self._queue.put(item)
