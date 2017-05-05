# -*- coding:utf-8 -*-
'''
Created on 2015年12月28日

@author: chenyitao
'''

import urlparse
from scrapy.spidermiddlewares import httperror
from scrapy import signals
import scrapy
from scrapy.exceptions import DontCloseSpider
from scrapy.http import Request
from common.queues import UNUSEFUL_PROXY_FEEDBACK_QUEUE
from base.models.task import Task

SIGNAL_STORAGE = object()

class SingleSpider(scrapy.Spider):
    '''
    single spider
    '''
    name = 'SingleSpider'
    start_urls = []

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(SingleSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.signal_dispatcher, signals.spider_opened)
        crawler.signals.connect(spider.signal_dispatcher, signals.spider_idle)
        crawler.signals.connect(spider.signal_dispatcher, signals.spider_error)
        return spider

    def __init__(self, callback=None):
        '''
        params[0]:callback 
        '''
        super(SingleSpider, self).__init__()
        self.signals_callback = callback

    def add_task(self, task):
        print('Add New Task: ' + task.url)
        url = task.url
        url_info = urlparse.urlparse(url)
        headers_data = {'Host': 'www.cheok.com',
                        'Upgrade-Insecure-Requests': 1,
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Encoding': 'gzip, deflate, sdch',
                        'Cookie': None,
                        'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
                        'Referer': url_info[0]+'://'+url_info[1]}
        req = Request(url,
                      method=task.method,
                      headers=headers_data,
                      callback=self.parse,
                      errback=self.error_back,
                      meta={'item': task},
                      dont_filter=True)
        self.crawler.engine.schedule(req, self)

    def error_back(self, response):
        task = response.request.meta['item']
        print('Failed: [%s][%s] . Will Retry After While' % (task.platform, task.row_key))
        self.add_task(task)
        proxy = response.request.meta.get('proxy', None)
        if response.type == httperror.HttpError:
            status = response.value.response.status
            if status >= 500:
                return
        proxy = proxy.split('//')[1]
        UNUSEFUL_PROXY_FEEDBACK_QUEUE.put([task.platform, proxy])
        
    def parse(self, response):
        task = response.request.meta.get('item')
        rsp_info = {'rsp': [response.url, response.status],
                    'content': response.body}
        if self.signals_callback:
            task.status = Task.Status.CRAWL_SUCCESS
            self.signals_callback(self, SIGNAL_STORAGE, [task, rsp_info])

    def signal_dispatcher(self, signal):
        '''
        callback signal
        '''
        if self.signals_callback:
            if signal == signals.spider_idle or signal == signals.spider_error:
                raise DontCloseSpider('..I prefer live spiders.')
            elif signal == signals.spider_opened:
                self.signals_callback(self, signal, self)
