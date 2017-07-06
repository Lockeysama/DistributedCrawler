# -*- coding: utf-8 -*-
'''
Created on 2017年6月30日

@author: chenyitao
'''

from ..model_base import QuickModelBase
import time
import random

import settings


class ExceptionType(object):

    class Crawler(object):
        CLIENT = 1101
        TASK_FAILED = 1201
        STORAGE_FAILED = 1301
        STORAGER_EXCEPTION = 1302
        PROXY = 1401
        NO_COOKIES = 1501
        COOKIES_INVALIDATE = 1502

    class Parser(object):
        CLIENT = 2101
        TASK_FAILED = 2201
        TASK_NO_PARSE_MODEL = 2202
        STORAGE_FAILED = 2301
        STORAGER_EXCEPTION = 2302

    class ProxyChecker(object):
        CLIENT = 3101
        STORAGE_FAILED = 3301
        STORAGER_EXCEPTION = 3302
        NO_SRC_PROXY = 3601
        CHECKE_FAILED = 3701


class ExceptionModelBase(QuickModelBase):
    '''
    classdocs
    '''

    EXCEPTION_TYPE = None

    def __init__(self, **kwargs):
        super(ExceptionModelBase, self).__init__(**kwargs)
        self.timestamp = kwargs.get('timestamp', time.time())
        self.id = kwargs.get('id', '{client_id}-{timestamp}-{rdm}'.format(client_id=settings.CLIENT_ID,
                                                                          timestamp=self.timestamp,
                                                                          rdm=random.randint(0, 10000)))
        self.code = kwargs.get('code', self.EXCEPTION_TYPE)
        self.name = kwargs.get('name', str(self.__class__).split('\'')[1].split('.')[-1])
        self.desc = kwargs.get('desc')

    @staticmethod
    def members():
        return dict(QuickModelBase.members(),
                    **{'id': None,
                       'code': None,
                       'name': None,
                       'desc': None,
                       'timestamp': None})
