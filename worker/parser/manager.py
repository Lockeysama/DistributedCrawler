# -*- coding: utf-8 -*-
'''
Created on 2017年4月14日

@author: chenyitao
'''

import setproctitle
import gevent

from log import TDDCLogging
from .models_manager import ParseModelsManager
from .parser import Parser
from .task import ParseTaskManager
from .storager import ParseStorager


class ParserManager(object):
    
    def __init__(self):
        TDDCLogging.info('->Client Is Starting')
        self._storager = ParseStorager()
        self._rules_updater = ParseModelsManager()
        self._parser = Parser(self._rules_updater.get_parse_model)
        self._task_manager = ParseTaskManager()
        TDDCLogging.info('->Client Was Ready.')
    
    @staticmethod
    def start():
        setproctitle.setproctitle("TDDC_PARSER")
        ParserManager()
        while True:
            gevent.sleep(15)


def main():
    setproctitle.setproctitle("TDDC_PARSER")
    ParserManager.start()
    
if __name__ == '__main__':
    main()
