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
import twisted.internet.error as internet_err
import twisted.web._newclient as newclient_err

from common.queues import UNUSEFUL_PROXY_FEEDBACK_QUEUE, TASK_STATUS_REMOVE_QUEUE
from common.models import Task
from common import TDDCLogging

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
            TDDCLogging.debug('Add New Task: ' + task.url)
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
        proxy = response.request.meta.get('proxy', None)
        if response.type == httperror.HttpError:
            status = response.value.response.status
            if status >= 500:
                fmt = '[%s][%s] Crawled Failed(%d | %s). Will Retry After While.' % proxy
                TDDCLogging.warning(fmt % (task.platform,
                                           task.url,
                                           status))
                self.add_task(task, True)
                return
            elif status == 404:
                retry_times = task.retry if task.retry else 3
                if times >= retry_times:
                    # TODO Exception
                    TASK_STATUS_REMOVE_QUEUE.put(task)
                    fmt = '[%s:%s] Crawled Failed(404 | %s). Not Retry.' % proxy
                    TDDCLogging.warning(fmt % (task.platform,
                                               task.url))
                    return
                times += 1
                fmt = '[%s:%s] Crawled Failed(%d | %s). Will Retry After While.' % proxy
                TDDCLogging.warning(fmt % (task.platform,
                                           task.url,
                                           status))
                self.add_task(task, True, times)
                return
        elif response.type == internet_err.TimeoutError:
            err_msg = 'TimeoutError'
        elif response.type in [internet_err.ConnectionRefusedError,
                               internet_err.TCPTimedOutError]:
            err_msg = '%d:%s' % (response.value.osError, response.value.message)
        elif response.type == newclient_err.ResponseNeverReceived:
            err_msg = 'ResponseNeverReceived'
        else:
            err_msg = '%s' % (response.value)
        if proxy:
            proxy = proxy.split('//')[1]
            UNUSEFUL_PROXY_FEEDBACK_QUEUE.put([task.platform, proxy])
        fmt = '[%s][%s] Crawled Failed(%s | %s). Will Retry After While.' % proxy
        TDDCLogging.warning(fmt % (task.platform,
                                   task.url,
                                   err_msg))
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
