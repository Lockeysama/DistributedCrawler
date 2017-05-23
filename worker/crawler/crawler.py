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
crawler_process = CrawlerProcess(settings)
crawler_process.join()

from conf import CrawlerSite
from common.queues import CrawlerQueues
from common import TDDCLogging

from .event import EventManagre, TDDCEvent
from .Scrapy import SingleSpider


class Crawler(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        TDDCLogging.info('-->Spider Is Starting.')
        self._spider = None
        self._spider_mqs = None
        self._signals_list = {signals.spider_opened: self._spider_opened,
                              SingleSpider.SIGNAL_STORAGE: self._storage}
        self._process = crawler_process
        self._process.crawl(SingleSpider, callback=self._spider_signals)
        EventManagre().register(TDDCEvent.RULE_UPDATE, self._rule_update)
        
    def _rule_update(self, event):
        print(event.__dict__)
        
    def _get_spider_mqs_size(self):
        return len(self._spider_mqs) if self._spider_mqs else 0
    
    def _task_dispatch(self):
        while True:
            if self._get_spider_mqs_size() < CrawlerSite.CONCURRENT / 4:
                while True:
                    task = CrawlerQueues.CRAWL.get()
                    self._spider.add_task(task)
                    if self._get_spider_mqs_size() >= CrawlerSite.CONCURRENT:
                        break
            else:
                gevent.sleep(1)
    
    def _spider_signals(self, spider, signal, params=None):
        if signal not in self._signals_list.keys():
            return
        func = self._signals_list.get(signal, None)
        if func:
            func(params)
  
    def _spider_opened(self, spider):
        if not self._spider:
            self._spider = spider
            self._spider_mqs = spider.crawler.engine.slot.scheduler.mqs
            gevent.spawn(self._task_dispatch)
            gevent.sleep()
            TDDCLogging.info('-->Spider Was Ready.')

    def _storage(self, items=None):
        CrawlerQueues.STORAGE.put(items)


def main():
    Crawler()
    while True:
        gevent.sleep(60)

if __name__ == '__main__':
    main()