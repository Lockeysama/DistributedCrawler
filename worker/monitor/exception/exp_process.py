# -*- coding: utf-8 -*-
'''
Created on 2017年7月25日

@author: chenyitao
'''

import importlib

import gevent

from common.log.logger import TDDCLogging
from common.queues.monitor import MonitorQueues


class ExceptionProcess(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self._exception_process = {}
        self._load_exception_models()
        gevent.spawn(self._processing)
        gevent.sleep()

    def _load_exception_models(self):
        base = 'worker.monitor.exception.process_models'
        models_packages = (base + '.crawler',)
        for package in models_packages:
            module = importlib.import_module(package)
            if not module:
                return
            for mould in dir(module):
                if len(mould) < len('EP') or mould[-len('EP'):] != 'EP':
                    continue
                cls = getattr(module, mould)
                if not cls:
                    continue
                self._exception_process[cls.EXCEPTION_TYPE] = cls

    def _processing(self):
        while True:
            exception = MonitorQueues.EXCEPTION.get()
            cls = self._exception_process.get(exception.EXCEPTION_TYPE)
            if not cls:
                TDDCLogging.error('No Match Exception Process Module.')
                continue
            cls(exception)
