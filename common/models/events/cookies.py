# -*- coding: utf-8 -*-
'''
Created on 2017年5月24日

@author: chenyitao
'''

from .event_base import EventBase, EventType


class CookiesGeneratorModuleEvent(EventBase):

    event_type = EventType.CookiesGenerator.MODULE
