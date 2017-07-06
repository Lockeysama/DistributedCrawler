# -*- coding: utf-8 -*-
'''
Created on 2017年7月3日

@author: chenyitao
'''

from common.models.exception.base import ExceptionType

class CrawlerClientEP(object):
    '''
    Crawler Client Exception Process.
    '''

    EXCEPTION_TYPE = ExceptionType.Crawler.CLIENT

    def __init__(self, exception):
        self._exception = exception
    