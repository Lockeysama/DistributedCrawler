# -*- coding: utf-8 -*-
'''
Created on 2017年5月24日

@author: chenyitao
'''

import random
import time

from ..model_base import QuickModelBase


class EventBase(QuickModelBase):

    EVENT_TYPE = None

    def __init__(self, **kwargs):
        super(EventBase, self).__init__(**kwargs)
        self.timestamp = kwargs.get('timestamp', time.time())
        self.id = kwargs.get('id', '{client_id}-{timestamp}-{rdm}'.format(client_id=1,
                                                                          timestamp=self.timestamp,
                                                                          rdm=random.randint(0, 10000)))
        self.event_type = kwargs.get('event_type', self.EVENT_TYPE)
        if not self.members().get('name'):
            self.name = kwargs.get('name', str(self.__class__).split('\'')[1].split('.')[-1])
        if not self.members().get('desc'):
            self.desc = kwargs.get('desc')

    @staticmethod
    def members():
        return dict(QuickModelBase.members(),
                    **{'id': None,
                       'timestamp': None,
                       'event_type': None,
                       'name': None,
                       'desc': None,
                       'event': None})
