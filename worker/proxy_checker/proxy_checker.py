# -*- coding: utf-8 -*-
'''
Created on 2017年4月17日

@author: chenyitao
'''

import gevent
from gevent import monkey
from worker.proxy_checker.proxy_src_updater import ProxySourceUpdater
from conf.proxy_checker_site import IS_PROXY_SOURCE_PROCESS_START
from worker.proxy_checker.proxy_rules_updater import ProxyCheckerRulesUpdater
monkey.patch_all()
import multiprocessing

from conf.base_site import STATUS

from worker.proxy_checker.proxy_manager import ProxyManager
from worker.proxy_checker.checker_manager import CheckerManager

class ProxyChecker(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self._checker_manager_tag = 1
        self._rules_updater_tag = 2
        self._tags_num = self._checker_manager_tag + self._rules_updater_tag
        self._cur_tags_num = 0
        self._proxy_manager = None
        self._checker = CheckerManager(self._checker_ready)
        self._rules_updater = ProxyCheckerRulesUpdater(self._rules_ready)

    def _start_proxy_manager(self, tag):
        self._cur_tags_num += tag
        if self._cur_tags_num == self._tags_num:
            self._proxy_manager = ProxyManager(self._proxy_manager_ready)

    def _proxy_manager_ready(self):
        print('->Client Was Ready.')
    
    def _rules_ready(self):
        self._start_proxy_manager(self._rules_updater_tag)
    
    def _checker_ready(self):
        self._start_proxy_manager(self._checker_manager_tag)
    
    @staticmethod
    def update_ip_source():
        ProxySourceUpdater().start()
    
    @staticmethod
    def start():
        ProxyChecker()
        if IS_PROXY_SOURCE_PROCESS_START:
            multiprocessing.Process(target=ProxyChecker.update_ip_source,
                                    name='ip_source_updater').start()
        while STATUS:
            gevent.sleep(15)


def main():
    pass
    
if __name__ == '__main__':
    main()
