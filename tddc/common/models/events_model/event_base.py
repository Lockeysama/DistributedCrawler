# -*- coding: utf-8 -*-
'''
Created on 2017年5月24日

@author: chenyitao
'''

from ..model_base import QuickModelBase


class EventBase(QuickModelBase):

    event_type = None

    @staticmethod
    def members():
        return dict(QuickModelBase.members(),
                    **{'id': None,
                       'timestamp': None,
                       'table': None,
                       'platform': None,
                       'method': None})
