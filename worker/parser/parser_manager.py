# -*- coding: utf-8 -*-
'''
Created on 2017年4月14日

@author: chenyitao
'''

import setproctitle
import gevent

from .updater import ParserRulesUpdater
from .parser import Parser
from .task import ParseTaskManager
from .storager import ParseDBManager
from common import TDDCLogging


class ParserManager(object):
    
    def __init__(self):
        TDDCLogging.info('->Client Is Starting')
        self._parser_manager = Parser()
        self._parse_db_manager = ParseDBManager()
        self._parser_rules_updater = ParserRulesUpdater()
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
