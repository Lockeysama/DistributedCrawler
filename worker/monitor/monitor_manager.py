# -*- coding: utf-8 -*-
'''
Created on 2017年5月17日

@author: chenyitao
'''

from log import TDDCLogging
from worker.monitor.exception.exception_manager import ExceptionManager
from worker.monitor.status.status_manager import StatusManager
import gevent

class MonitorManager(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        TDDCLogging.info('->Exception Manager Is Starting.')
        self._exception_manager = ExceptionManager()
        self._status_manager = StatusManager()
        TDDCLogging.info('->Exception Manager Was Started.')

    @staticmethod
    def start():
        MonitorManager()
        while True:
            gevent.sleep(60)
        
def main():
    pass

if __name__ == '__main__':
    main()
