# -*- coding: utf-8 -*-
'''
Created on 2017年4月14日

@author: chenyitao
'''

import gevent

from scrapy.utils.project import get_project_settings
from worker.crawler.event import EventManagre, TDDCEvent
import logging
settings = get_project_settings()
from scrapy import signals
from scrapy.crawler import CrawlerProcess
from Scrapy.spiders.single_spider import SingleSpider, SIGNAL_STORAGE

from conf.base_site import STATUS
from conf.crawler_site import CRAWLER_CONCURRENT
from common.queues import CRAWL_QUEUE, STORAGE_QUEUE


crawler_process = CrawlerProcess(settings)
crawler_process.join()


class Crawler(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        print('-->Spider Is Starting.')
        self._spider = None
        self._signals_list = {signals.spider_opened: self._spider_opened,
                              SIGNAL_STORAGE: self._storage}
        self._process = crawler_process
        self._process.crawl(SingleSpider, callback=self._spider_signals)
        EventManagre().register(TDDCEvent.RULE_UPDATE, self._rule_update)
        
    def _rule_update(self, event):
        print(event.__dict__)
        
    def _get_spider_mqs_size(self):
        q = self._spider.crawler.engine.slot.scheduler.mqs.queues
        mqs_count = len(q[0]) if q and len(q) else 0
        return mqs_count
    
    def _task_dispatch(self):
        while STATUS:
            if self._get_spider_mqs_size() < CRAWLER_CONCURRENT/2:
                while True:
                    task = CRAWL_QUEUE.get()
                    self._spider.add_task(task)
                    if self._get_spider_mqs_size() >= CRAWLER_CONCURRENT:
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
            gevent.spawn(self._task_dispatch)
            gevent.sleep()
            print('-->Spider Was Ready.')
            logging.getLogger().setLevel(logging.WARNING)

    def _storage(self, items=None):
        STORAGE_QUEUE.put(items)


def main():
    Crawler()
    while True:
        gevent.sleep(60)

if __name__ == '__main__':
    main()