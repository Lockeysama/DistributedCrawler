# -*- coding: utf-8 -*-
'''
Created on 2017年4月14日

@author: chenyitao
'''

import setproctitle
import logging
from worker.parser.parse_rules_updater import SIGNAL_RULES_UPDATER_READY,\
    ParserRulesUpdater
logging.basicConfig(filename='tddc_p.log')
import gevent
from gevent import monkey
monkey.patch_all(socket=False)

from worker.parser.parser_manager import SIGNAL_PARSER_READY, ParserManager
from worker.parser.parse_task_manager import ParseTaskManager,\
    SIGNAL_TASK_MANAGER_READY
from worker.parser.parse_db_manager import ParseDBManager, SIGNAL_DB_READY


class Parser(object):
    
    def __init__(self):
        print('->Client Is Starting')
        self._signals_list = {SIGNAL_PARSER_READY: self._parser_ready,
                              SIGNAL_DB_READY: self._db_ready,
                              SIGNAL_TASK_MANAGER_READY: self._task_manager_ready,
                              SIGNAL_RULES_UPDATER_READY: self._parser_rules_updater_ready}
        self._parser_tag = 1
        self._db_tag = 2
        self._rules_updater_tag = 3
        self._tags_num = 1 + 2 + 3
        self._cur_tags_num = 0
        self._task_manager = None
        self._parser_manager = ParserManager(self._parser_signals)
        self._parse_db_manager = ParseDBManager(self._parser_signals)
        self._parser_rules_updater = ParserRulesUpdater(self._parser_signals)
    
    @staticmethod
    def start():
        setproctitle.setproctitle("TDDC_PARSER")
        Parser()
        while True:
            gevent.sleep(15)
        
    def _parser_signals(self, instance, signal, params=None):
        if signal not in self._signals_list.keys():
            return
        func = self._signals_list[signal]
        if func:
            func(params)

    def _start_task_manager(self, tag):
        self._cur_tags_num += tag
        if self._cur_tags_num == self._tags_num:
            self._task_manager = ParseTaskManager(self._parser_signals)

    def _parser_ready(self, parser):
        self._start_task_manager(self._parser_tag)
    
    def _db_ready(self, db):
        self._start_task_manager(self._db_tag)
    
    def _parser_rules_updater_ready(self, updater):
        self._start_task_manager(self._rules_updater_tag)
        
    def _task_manager_ready(self, task_manager):
        print('->Client Was Ready.')
    
    def __del__(self):
        print('del', self.__class__)


def main():
    setproctitle.setproctitle("TDDC_PARSER")
    Parser.start()
    
if __name__ == '__main__':
    main()
