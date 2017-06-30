# -*- coding: utf-8 -*-
'''
Created on 2017年4月12日

@author: chenyitao
'''

from .base_site import BaseSite, CLIENT_ID, get_mac_address


class ParserSite(BaseSite):
    
    # Parse Rules HBase Table Info
    RULES_TABLE = 'tddc_p_rules'
    RULES_FAMILY = 'rules'
    RULES_QUALIFIER = 'index'
    
    # Parse Event Topic Info
    EVENT_TOPIC = 'tddc_p_event'
    EVENT_TOPIC_GROUP = 'tddc.p.{mac}.{id}'.format(mac=get_mac_address(), id=CLIENT_ID)
    
    # Parse Task Topic Info
    PARSE_TOPIC_GROUP = 'tddc.p.parser'
    
    # Parser Concurrent
    FETCH_SOURCE_CONCURRENT = 8
