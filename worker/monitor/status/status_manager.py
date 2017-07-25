# -*- coding: utf-8 -*-
'''
Created on 2017年5月17日

@author: chenyitao
'''

from common import TDDCLogging
from worker.monitor.status.task_status import TaskStatusMonitor


class StatusManager(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        TDDCLogging.info('-->Status Manager Is Starting.')
        self._task_status_monitor = TaskStatusMonitor()
        TDDCLogging.info('-->Status Manager Was Started.')


def main():
    import gevent.monkey
    gevent.monkey.patch_all()
    StatusManager()
    while True:
        gevent.sleep(10)

if __name__ == '__main__':
    main()
