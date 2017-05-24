# -*- coding: utf-8 -*-
'''
Created on 2017年5月24日

@author: chenyitao
'''

from .event_base import EventBase, EventType


class CrawlerBaseDataEvent(EventBase):

    event_type = EventType.Crawler.BASE_DATA


class ParserBaseDataEvent(EventBase):

    event_type = EventType.Parser.BASE_DATA


class ProxyCheckerBaseDataEvent(EventBase):

    event_type = EventType.ProxyChecker.BASE_DATA


class CookiesGeneratorBaseDataEvent(EventBase):

    event_type = EventType.CookiesGenerator.BASE_DATA


class MonitorBaseDataEvent(EventBase):

    event_type = EventType.Monitor.BASE_DATA
