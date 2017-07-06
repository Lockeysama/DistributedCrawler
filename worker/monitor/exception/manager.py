# -*- coding: utf-8 -*-
'''
Created on 2017年5月17日

@author: chenyitao
'''

import importlib

import gevent

from common import TDDCLogging
from common.queues.monitor import MonitorQueues

from .exception import ExceptionMessageSR


class ExceptionManager(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        TDDCLogging.info('-->Exception Manager Is Starting.')
        self._exception_process = {}
        self._load_exception_models()
        self._task_manager = ExceptionMessageSR()
        gevent.spawn(self._process)
        gevent.sleep()
        TDDCLogging.info('-->Exception Manager Was Started.')

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

    def _process(self):
        while True:
            exception = MonitorQueues.EXCEPTION.get()
            cls = self._exception_process.get(exception.code)
            if not cls:
                TDDCLogging.warning('No Match Process To Exception: {exp_id}'.format(exp_id=exception.id))
                continue
            cls(exception)

        
def main():
    pass

if __name__ == '__main__':
    main()
