# -*- coding: utf-8 -*-
'''
Created on 2017年4月17日

@author: chenyitao
'''


import setproctitle
import logging
logging.basicConfig(filename='tddc_p.log')

import gevent
from gevent import monkey
monkey.patch_all()


from worker.proxy_checker.proxy_rules_updater import ProxyCheckerRulesUpdater
from worker.proxy_checker.proxy_mq_manager import ProxyMQManager
from worker.proxy_checker.proxy_manager import ProxyManager
from worker.proxy_checker.proxy_checker_manager import CheckerManager


class ProxyChecker(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        setproctitle.setproctitle("TDDC_PROXY_CHECKER")
        print('->Client Is Starting')
        self._proxy_manager = None
        self._cur_tags_num = 0
        self._checker_manager_tag = 1
        self._rules_updater_tag = 2
        self._proxy_mq_tag = 3
        self._tags_num = self._checker_manager_tag + self._rules_updater_tag + self._proxy_mq_tag
        self._checker = CheckerManager(self._checker_ready)
        self._rules_updater = ProxyCheckerRulesUpdater(self._rules_ready)
        self._proxy_mq_manager = ProxyMQManager(self._proxy_mq_manager_ready)

    def _start_proxy_manager(self, tag):
        self._cur_tags_num += tag
        if self._cur_tags_num == self._tags_num:
            self._proxy_manager = ProxyManager(self._proxy_manager_ready)

    def _proxy_manager_ready(self):
        print('->Client Was Ready.')
    
    def _proxy_mq_manager_ready(self):
        self._start_proxy_manager(self._proxy_mq_tag)
        
    def _rules_ready(self):
        self._start_proxy_manager(self._rules_updater_tag)
    
    def _checker_ready(self):
        self._start_proxy_manager(self._checker_manager_tag)
    
    @staticmethod
    def start():
        ProxyChecker()
        while True:
            gevent.sleep(15)


def main():
    setproctitle.setproctitle("TDDC_PROXY_CHECKER")
    ProxyChecker.start()
    
if __name__ == '__main__':
    main()
