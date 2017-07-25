# -*- coding: utf-8 -*-
'''
Created on 2017年6月30日

@author: chenyitao
'''

from .base import ExceptionModelBase, ExceptionType, settings


class CrawlerClientException(ExceptionModelBase):

    EXCEPTION_TYPE = ExceptionType.Crawler.CLIENT

    @staticmethod
    def members():
        return dict(ExceptionModelBase.members(),
                    **{'client_id': settings.CLIENT_ID})

class CrawlerTaskFailedException(ExceptionModelBase):

    EXCEPTION_TYPE = ExceptionType.Crawler.TASK_FAILED

    def __init__(self, **kwargs):
        super(CrawlerTaskFailedException, self).__init__(**kwargs)
        self.task = kwargs.get('task', None) if kwargs.get('task') else None 

    @staticmethod
    def members():
        return dict(ExceptionModelBase.members(),
                    **{'task': None})

class CrawlerSrorageFailedException(ExceptionModelBase):

    EXCEPTION_TYPE = ExceptionType.Crawler.STORAGE_FAILED


class CrawlerStoragerException(ExceptionModelBase):

    EXCEPTION_TYPE = ExceptionType.Crawler.STORAGER_EXCEPTION


class CrawlerProxyException(ExceptionModelBase):

    EXCEPTION_TYPE = ExceptionType.Crawler.PROXY


class CrawlerNoCookiesException(ExceptionModelBase):

    EXCEPTION_TYPE = ExceptionType.Crawler.NO_COOKIES


class CrawlerCookiesInvalidateException(ExceptionModelBase):

    EXCEPTION_TYPE = ExceptionType.Crawler.COOKIES_INVALIDATE
