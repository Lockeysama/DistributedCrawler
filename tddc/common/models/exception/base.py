# -*- coding: utf-8 -*-
'''
Created on 2017年6月30日

@author: chenyitao
'''

from ..model_base import QuickModelBase
import time
import random


class ExceptionModelBase(QuickModelBase):
    '''
    classdocs
    '''

    EXCEPTION_TYPE = None

    def __init__(self, **kwargs):
        super(ExceptionModelBase, self).__init__(**kwargs)
        self.timestamp = kwargs.get('timestamp', time.time())
        self.id = kwargs.get('id', '{client_id}-{timestamp}-{rdm}'.format(client_id=1,
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
