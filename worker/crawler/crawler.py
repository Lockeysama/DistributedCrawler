# -*- coding: utf-8 -*-
'''
Created on 2017年4月14日

@author: chenyitao
'''

import setproctitle
from gevent import monkey
monkey.patch_all()
import logging
logging.basicConfig(filename='tddc_c.log')

from twisted.internet import reactor

from worker.crawler.crawl_db_manager import CrawlDBManager
from worker.crawler.crawler_proxy_manager import CrawlerProxyManager
from worker.crawler.crawl_task_manager import CrawlTaskManager
from worker.crawler.crawler_manager import CrawlerManager


class Crawler(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        setproctitle.setproctitle("TDDC_CRAWLER")
        self._task_manager = None
        self._crawl_tag = 1
        self._db_tag = 2
        self._proxy_tag = 3
        self._tags_num = self._crawl_tag + self._db_tag + self._proxy_tag
        self._cur_tags_num = 0
        self._task_manager = None
        self._crawler_manager = CrawlerManager(self._crawler_ready)
        self._crawl_db_manager = CrawlDBManager(self._db_manager_ready)
        self._crawler_proxy_manager = CrawlerProxyManager(self._proxy_manager_ready)
        
    @staticmethod
    def start():
        reactor.__init__()  # @UndefinedVariable
        Crawler()
        reactor.run()  # @UndefinedVariable
        
    def _crawler_ready(self, crawler):
        self._start_task_manager(self._crawl_tag)

    def _db_manager_ready(self, db_manager):
        self._start_task_manager(self._db_tag)

    def _proxy_manager_ready(self, proxy_manager):
        self._start_task_manager(self._proxy_tag)

    def _start_task_manager(self, call_tag):
        self._cur_tags_num += call_tag
        if self._cur_tags_num == self._tags_num:
            self._task_manager = CrawlTaskManager(self._task_manager_ready)

    def _task_manager_ready(self, task_manager):
        print('->Client Was Ready.')
    
    def __del__(self):
        print('del', self.__class__)

        
def main():
    Crawler.start()

if __name__ == '__main__':
    main()