# -*- coding: utf-8 -*-
'''
Created on 2017年4月14日

@author: chenyitao
'''

from .base_site import BaseSite
from common import get_mac_address


class CrawlerSite(BaseSite):

    # Crawler ID
    CLIENT_ID = 1

    # Crawler Concurrent
    CONCURRENT = 100
    
    # Crawler Topic Group
    CRAWL_TOPIC_GROUP = 'tddc.crawler'
    
    # Proxy Checker Event Topic Info
    EVENT_TOPIC = 'tddc_c_event'
    EVENT_TOPIC_GROUP = 'tddc.pc.{mac}.{id}'.format(mac=get_mac_address(),
                                                    id=CLIENT_ID) 
