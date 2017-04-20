# -*- coding: utf-8 -*-
'''
Created on 2017年4月17日

@author: chenyitao
'''

import gevent
from gevent import monkey
from worker.proxy_checker.proxy_src_updater import ProxySourceUpdater
monkey.patch_all()
import multiprocessing

from conf.base_site import STATUS

from worker.proxy_checker.proxy_db_manager import ProxyDBManager
from worker.proxy_checker.checker_manager import CheckerManager

class ProxyChecker(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self._cache = ProxyDBManager(self._db_manager_ready)
        self._checker = CheckerManager(self._checker_ready)
        # Rules
        
    def _db_manager_ready(self):
        pass
    
    def _rules_ready(self):
        pass
    
    def _checker_ready(self):
        pass
    
    @staticmethod
    def update_ip_source():
        ProxySourceUpdater().start()
    
    @staticmethod
    def start():
        multiprocessing.Process(target=ProxyChecker.update_ip_source, name='ip_source_updater').start()
        ProxyChecker()
        while STATUS:
            gevent.sleep(15)


def main():
    pass
    
if __name__ == '__main__':
    main()
