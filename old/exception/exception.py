# -*- coding: utf-8 -*-
'''
Created on 2017年5月5日

@author: chenyitao
'''

from tddc.redis.record import RecordManager

from tddc.config.config_center import ConfigCenter
from tddc.kafka.producer import KeepAliveProducer
from tddc.log.logger import TDDCLogger
from tddc.util.util import Singleton, object2json
from tddc.worker.status import StatusManager


class ExceptionCollection(TDDCLogger):
    '''
    classdocs
    '''

    __metaclass__ = Singleton

    def __init__(self):
        super(ExceptionCollection, self).__init__()
        self.info('Exception Collector Is Starting.')
        self._exception_info = ConfigCenter().get_exception()
        self._exception_producer = KeepAliveProducer()
        self.info('Exception Collector Was Started.')

    def push(self, exception):
        RecordManager().create_record('tddc.exception.record',
                                      exception.id,
                                      object2json(exception))
        StatusManager().update_status('tddc.exception.status.%d.' % exception.exception_type,
                                      exception.id,
                                      1)
        self._exception_producer.send(self._exception_info.topic,
                                      object2json(exception))
