# -*- coding:utf-8 -*-
'''
Created on 2015年12月28日

@author: chenyitao
'''

from string import upper
import time
import urlparse

from scrapy import signals
import scrapy
from scrapy.exceptions import DontCloseSpider
from scrapy.http import Request, FormRequest
from scrapy.spidermiddlewares import httperror

from common import TDDCLogging
from common.models.exception.crawler import CrawlerTaskFailedException
from common.queues import CrawlerQueues
import twisted.internet.error as internet_err
import twisted.web._newclient as newclient_err
from worker.crawler.cookies import CookiesManager


class SingleSpider(scrapy.Spider):
    '''
    single spider
    '''

    SIGNAL_STORAGE = object()

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
        headers = self._init_request_headers(task)
        req = (self._make_get_request(task, headers, times) 
               if not task.method or upper(task.method) == 'GET' 
               else self._make_post_request(task, headers, times))
        self.crawler.engine.schedule(req, self)
        task.timestamp = time.time()
        CrawlerQueues.TASK_STATUS.put(task)

    def _make_get_request(self, task, headers, times):
        req = Request(task.url,
                      headers=headers,
                      cookies=task.cookie or CookiesManager.get_cookie(task.platform),
                      callback=self.parse,
                      errback=self.error_back,
                      meta={'item': [task, times]},
                      dont_filter=True)
        return req

    def _make_post_request(self, task, headers, times):
        form_data = {'params': headers.get('post_params', None)}
        req = FormRequest(task.url,
                          formdata=form_data,
                          headers=headers,
                          cookies=task.cookie or CookiesManager.get_cookie(task.platform),
                          callback=self.parse,
                          errback=self.error_back,
                          meta={'item': [task, times]},
                          dont_filter=True)
        return req

    def error_back(self, response):
        task, times = response.request.meta['item']
        proxy = response.request.meta.get('proxy', None)
        if response.type == httperror.HttpError:
            status = response.value.response.status
            if status >= 500 or status in [408, 429]: 
                fmt = ('[%s][%s] Crawled Failed(\033[0m %d \033[1;37;43m| %s ). '
                       'Will Retry After While.')
                TDDCLogging.warning(fmt % (task.platform,
                                           task.url,
                                           status,
                                           proxy))
                self.add_task(task, True)
                return
            elif status == 404:
                retry_times = task.retry if task.retry else 3
                if times >= retry_times:
                    exception = CrawlerTaskFailedException(task)
                    CrawlerQueues.EXCEPTION.put(exception)
                    CrawlerQueues.TASK_STATUS_REMOVE.put(task)
                    fmt = ('[%s:%s] Crawled Failed(\033[0m 404 \033[1;37;43m| %s ). '
                           'Not Retry.')
                    TDDCLogging.warning(fmt % (task.platform,
                                               task.url,
                                               proxy))
                    return
                times += 1
                fmt = ('[%s:%s] Crawled Failed(\033[0m %d \033[1;37;43m| %s ). '
                       'Will Retry After While.')
                TDDCLogging.warning(fmt % (task.platform,
                                           task.url,
                                           status,
                                           proxy))
                self.add_task(task, True, times)
                return
            else:
                err_msg = '{status}'.format(status=status)
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
            CrawlerQueues.UNUSEFUL_PROXY_FEEDBACK.put([task.platform, proxy])
        fmt = ('[%s][%s] Crawled Failed(\033[0m %s \033[1;37;43m| %s ). '
               'Will Retry After While.')
        TDDCLogging.warning(fmt % (task.platform,
                                   task.url,
                                   err_msg,
                                   proxy))
        self.add_task(task, True, times)

    def parse(self, response):
#         TDDCLogging.debug('Download Success. ' + response.url)
        task,_ = response.request.meta.get('item')
        rsp_info = {'rsp': [response.url, response.status],
                    'content': response.body}
        if self.signals_callback:
            self.signals_callback(self, SingleSpider.SIGNAL_STORAGE, [task, rsp_info])

    def signal_dispatcher(self, signal):
        '''
        callback signal
        '''
        if self.signals_callback:
            if signal == signals.spider_idle or signal == signals.spider_error:
                if signal == signals.spider_error:
                    print('err')
                raise DontCloseSpider('..I prefer live spiders.')
            elif signal == signals.spider_opened:
                self.signals_callback(self, signal, self)
