# -*- coding: utf-8 -*-
'''
Created on 2017年4月14日

@author: chenyitao
'''

import setproctitle
from gevent import monkey
monkey.patch_all()
import logging
logging.basicConfig(filename='crawler.log')

from twisted.internet import reactor

from worker.crawler.exception import ExceptionCollection
from worker.crawler.storage import CrawlStorager
from worker.crawler.proxy_pool import CrawlProxyPool
from worker.crawler.task import CrawlTaskManager
from worker.crawler.crawler import Crawler


class CrawlerManager(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        setproctitle.setproctitle("TDDC_CRAWLER")
        print('->Crawler Starting.')
        self._exception_collection = ExceptionCollection()
        self._crawler = Crawler()
        self._storager = CrawlStorager()
        self._proxy_pool = CrawlProxyPool()
        self._task_manager = CrawlTaskManager()
        print('->Crawler Was Ready.')
        
    @staticmethod
    def start():
        reactor.__init__()  # @UndefinedVariable
        CrawlerManager()
        reactor.run()  # @UndefinedVariable


def main():
    CrawlerManager.start()

if __name__ == '__main__':
    main()
