# -*- coding: utf-8 -*-
'''
Created on 2017年4月14日

@author: chenyitao
'''

import setproctitle
import gevent

from common import TDDCLogging
from .parser import Parser
from .task import ParseTaskManager
from .storager import ParseStorager
from base import WorkerManager


class ParserManager(WorkerManager):
    
    def __init__(self):
        TDDCLogging.info('->Client Is Starting')
        super(ParserManager, self).__init__()
        self._storager = ParseStorager()
        self._parser = Parser()
        self._task_manager = ParseTaskManager()
        TDDCLogging.info('->Client Was Ready.')
    
    @staticmethod
    def start():
        setproctitle.setproctitle("TDDC_PARSER")
        ParserManager()
        while True:
            gevent.sleep(15)


def main():
    ParserManager.start()
    
if __name__ == '__main__':
    main()
