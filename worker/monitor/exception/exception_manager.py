# -*- coding: utf-8 -*-
'''
Created on 2017年5月17日

@author: chenyitao
'''

from worker.monitor.exception.task import ExceptionTaskManager
from common import TDDCLogging

class ExceptionManager(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        TDDCLogging.info('-->Exception Manager Is Starting.')
        self._task_manager = ExceptionTaskManager()
        TDDCLogging.info('-->Exception Manager Was Started.')
    
        
def main():
    pass

if __name__ == '__main__':
    main()
