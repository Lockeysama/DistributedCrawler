# -*- coding: utf-8 -*-
'''
Created on 2017年4月14日

@author: chenyitao
'''

import setproctitle
from twisted.internet import reactor

from log import TDDCLogging

from .exception import ExceptionCollection
from .storager import CrawlStorager
from .proxy_pool import CrawlProxyPool
from .task import CrawlTaskManager
from .crawler import Crawler
from .cookies import CookiesManager


class CrawlerManager(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        setproctitle.setproctitle("TDDC_CRAWLER")
        TDDCLogging.info('->Crawler Starting.')
        self._exception_collection = ExceptionCollection()
        self._crawler = Crawler()
        self._storager = CrawlStorager()
        self._proxy_pool = CrawlProxyPool()
        self._cookies = CookiesManager()
        self._task_manager = CrawlTaskManager()
        TDDCLogging.info('->Crawler Was Ready.')
        
    @staticmethod
    def start():
        reactor.__init__()  # @UndefinedVariable
        CrawlerManager()
        reactor.run()  # @UndefinedVariable


def main():
    CrawlerManager.start()

if __name__ == '__main__':
    main()
