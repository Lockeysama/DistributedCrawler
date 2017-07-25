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
from worker.monitor.exception.exp_process import ExceptionProcess


class ExceptionManager(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        TDDCLogging.info('-->Exception Manager Is Starting.')
        self._exp_process = ExceptionProcess()
        self._task_manager = ExceptionMessageSR()
        TDDCLogging.info('-->Exception Manager Was Started.')

        
def main():
    pass

if __name__ == '__main__':
    main()
