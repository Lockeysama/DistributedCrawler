# -*- coding: utf-8 -*-
'''
Created on 2017年5月5日

@author: chenyitao
'''

from ..log.logger import TDDCLogger
from ..config.config_center import ConfigCenter
from ..kafka.producer import KeepAliveProducer
from ..redis.record import RecordManager
from ..redis.status import StatusManager
from ..util.util import Singleton, object2json


class ExceptionCollection(TDDCLogger):
    '''
    classdocs
    '''

    __metaclass__ = Singleton

    def __init__(self):
        super(ExceptionCollection, self).__init__()
        self.logger.info('-->Exception Collector Is Starting.')
        self._exception_info = ConfigCenter().get_exception()
        kafka_info = ConfigCenter().get_services('kafka')
        if not kafka_info:
            self.logger.error('Kafka Server Info Not Found.')
            return
        kafka_nodes = ','.join(['%s:%s' % (info.host, info.port) for info in kafka_info['kafka']])
        self._exception_producer = KeepAliveProducer(bootstrap_servers=kafka_nodes)
        self.logger.info('-->Exception Collector Was Started.')

    def push(self, exception):
        RecordManager().create_record('tddc.exception.record',
                                      exception.id,
                                      object2json(exception))
        StatusManager().update_status('tddc.exception.status.%d.' % exception.exception_type,
                                      exception.id,
                                      1)
        self._exception_producer.send(self._exception_info.topic,
                                      object2json(exception))
