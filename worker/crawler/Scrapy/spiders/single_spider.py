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
from common.queues import UNUSEFUL_PROXY_FEEDBACK_QUEUE, TASK_STATUS_REMOVE_QUEUE
from common.models.task import Task

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

    def _init_request_headers(self, task):
        iheaders = {}
        if not task.headers:
            url_info = urlparse.urlparse(task.url)
            task.headers = {'Host': url_info[1]}
        for k, v in task.headers.items():
            if not v:
                if k == 'Host':
                    url_info = urlparse.urlparse(task.url)
                    iheaders[k] = url_info[1]
                continue
            iheaders[k] = v
        return iheaders

    def add_task(self, task, is_retry=False, times=1):
        if not is_retry:
            print('Add New Task: ' + task.url)
        headers_data = self._init_request_headers(task)
        req = Request(task.url,
                      method=task.method if task.method else 'GET',
                      headers=headers_data,
                      callback=self.parse,
                      errback=self.error_back,
                      meta={'item': [task, times]},
                      dont_filter=True)
        self.crawler.engine.schedule(req, self)

    def error_back(self, response):
        task, times = response.request.meta['item']
        if response.type == httperror.HttpError:
            status = response.value.response.status
            if status >= 500:
                print('Failed: [%s][%s] . Will Retry After While' % (task.platform, task.row_key))
                self.add_task(task, True)
                return
            elif status == 404:
                retry_times = task.retry if task.retry else 3
                if times >= retry_times:
                    # TODO Exception
                    TASK_STATUS_REMOVE_QUEUE.put(task)
                    return
                times += 1
                print('Failed: [%s][%s] . Will Retry After While' % (task.platform, task.row_key))
                self.add_task(task, True, times)
                return
        proxy = response.request.meta.get('proxy', None)
        proxy = proxy.split('//')[1]
        UNUSEFUL_PROXY_FEEDBACK_QUEUE.put([task.platform, proxy])
        print('Failed: [%s][%s] . Will Retry After While' % (task.platform, task.row_key))
        self.add_task(task, True, times)
        
    def parse(self, response):
        task,_ = response.request.meta.get('item')
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
