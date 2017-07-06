# -*- coding: utf-8 -*-
'''
Created on 2017年5月17日

@author: chenyitao
'''

import importlib
import json

import gevent

from base import TaskManagerBase
from base.plugins.mq.kafka_manager.kafka_helper import KafkaHelper
from common import TDDCLogging
from common.queues.monitor import MonitorQueues
from conf import MonitorSite


class ExceptionMessageSR(TaskManagerBase):
    '''
    Exception Messages Send And Recv.
    '''
    
    topics = {}

    def __init__(self):
        '''
        Constructor
        '''
        TDDCLogging.info('--->Messages Send And Recv Plugin Is Starting.')
        super(ExceptionMessageSR, self).__init__(status_logger=False)
        self._models_table = {}
        self._load_exception_models()
        gevent.spawn(self._recv)
        gevent.sleep()
        TDDCLogging.info('--->Messages Send And Recv Plugin Was Ready.')

    def _load_exception_models(self):
        base = 'common.models.exception'
        models_packages = (base + '.crawler',
                           base + '.parser',
                           base + '.proxy_checker')
        for package in models_packages:
            module = importlib.import_module(package)
            if not module:
                return
            for mould in dir(module):
                if len(mould) < len('Exception') or mould[-len('Exception'):] != 'Exception':
                    continue
                cls = getattr(module, mould)
                if not cls:
                    continue
                self._models_table[cls.EXCEPTION_TYPE] = cls

    def _recv(self):
        self._consumer = KafkaHelper.make_consumer(MonitorSite.KAFKA_NODES,
                                                   MonitorSite.EXCEPTION_TOPIC,
                                                   MonitorSite.EXCEPTION_GROUP)
        while True:
            partition_records = self._consumer.poll(2000, 16)
            if not len(partition_records):
                gevent.sleep(1)
                continue
            for _, records in partition_records.items():
                for record in records:
                    self._record_proc(record)

    def _record_proc(self, record):
        try:
            exception = json.loads(record.value)
        except Exception, e:
            self._consume_msg_exp('PARSE_TASK_JSON_ERR', record.value, e)
        else:
            code = exception.get('code')
            if not code:
                TDDCLogging.warning('This Exception Is Not Type Of `ExceptionModel`.')
                return
            cls = self._models_table.get(code)
            if not cls:
                TDDCLogging.warning('This Exception Is No Match Model.')
                return
            MonitorQueues.EXCEPTION.put(cls(**exception))
