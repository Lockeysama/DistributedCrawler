# -*- coding: utf-8 -*-
'''
Created on 2017年4月17日

@author: chenyitao
'''


import setproctitle
import gevent
from gevent import monkey
monkey.patch_all()

from common import TDDCLogging
# from .rules_updater import ProxyCheckerRulesUpdater
from .event import ProxyMQManager
from .proxy import ProxyManager
from .checker import Checker


class ProxyCheckerManager(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        setproctitle.setproctitle("TDDC_PROXY_CHECKER")
        TDDCLogging.info('->Proxy Checker Is Starting')
        self._checker = Checker()
#         self._rules_updater = ProxyCheckerRulesUpdater()
        self._proxy_mq_manager = ProxyMQManager()
        self._proxy_manager = ProxyManager()
        TDDCLogging.info('->Proxy Checker Was Ready.')
    
    @staticmethod
    def start():
        ProxyCheckerManager()
        while True:
            gevent.sleep(15)


def main():
    ProxyCheckerManager.start()
    
if __name__ == '__main__':
    main()
