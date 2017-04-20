# -*- coding: utf-8 -*-
'''
Created on 2017年4月14日

@author: chenyitao
'''

import gevent

from scrapy.utils.project import get_project_settings
settings = get_project_settings()
from scrapy import signals
from scrapy.crawler import CrawlerProcess
from Scrapy.spiders.single_spider import SingleSpider, SIGNAL_STORAGE
from conf.base_site import STATUS
from conf.crawler_site import CRAWL_QUEUE_SWITCH
from common.queues import CRAWL_QUEUE, STORAGE_QUEUE


crawler_process = CrawlerProcess(settings)
crawler_process.join()

SIGNAL_CRAWLER_READY = object()

class CrawlerManager(object):
    '''
    classdocs
    '''

    def __init__(self, callback=None):
        '''
        Constructor
        '''
        self._callback = callback
        self._spider = None
        self._signals_list = {signals.spider_opened: self._spider_opened,
                              SIGNAL_STORAGE: self._storage}
        gevent.spawn(self._task_dispatch)
        gevent.sleep()
        self._process = crawler_process
        self._process.crawl(SingleSpider, callback=self._spider_signals)
        
    def _task_dispatch(self):
        while not self._spider:
            gevent.sleep(0.5)
        while STATUS:
            q = self._spider.crawler.engine.slot.scheduler.mqs.queues
            mqs_count = len(q) if q else 0
            if mqs_count < CRAWL_QUEUE_SWITCH:
                task = CRAWL_QUEUE.get()
                self._spider.add_task(task)
            else:
                gevent.sleep(0.5)
    
    def _spider_signals(self, spider, signal, params=None):
        if signal not in self._signals_list.keys():
            return
        func = self._signals_list[signal]
        if func:
            func(params)
  
    def _spider_opened(self, spider):
        self._spider = spider
        if self._callback:
            self._callback(self)
    
    def _storage(self, items=None):
        STORAGE_QUEUE.put(items)


def main():
    CrawlerManager()
    while True:
        gevent.sleep(60)

if __name__ == '__main__':
    main()