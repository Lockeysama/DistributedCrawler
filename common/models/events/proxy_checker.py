# -*- coding: utf-8 -*-
'''
Created on 2017年5月24日

@author: chenyitao
'''

from .event_base import EventBase, EventType


class ProxyCheckerModuleEvent(EventBase):

    event_type = EventType.ProxyChecker.MODULE


class ProxyCheckerSourceAPIEvent(EventBase):

    event_type = EventType.ProxyChecker.SOURCE
