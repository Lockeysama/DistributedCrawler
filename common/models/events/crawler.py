# -*- coding: utf-8 -*-
'''
Created on 2017年5月24日

@author: chenyitao
'''

from .event_base import EventBase, EventType


class CrawlerCookiesEvent(EventBase):

    event_type = EventType.Crawler.COOKIES


class CrawlerModuleEvent(EventBase):
    
    event_type = EventType.Crawler.MODULE
