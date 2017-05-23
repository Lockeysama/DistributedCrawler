# -*- coding: utf-8 -*-
'''
Created on 2017年4月17日

@author: chenyitao
'''

from .base_site import BaseSite
from common import get_mac_address


class ProxyCheckerSite(BaseSite):

    CLIENT_ID = 1

    # Is Proxy Source Process Start.
    PROXY_SOURCE_UPDATER_ENABLE = True
    
    # Proxy Checker Rules Conf Path Base
    RULES_CONF_PATH_BASE = './conf/proxy_checker_rule_index/'
    
    # Proxy Checker Rules HBase Table Info
    RULES_CONF_PATH = RULES_CONF_PATH_BASE + '%s.json'
    RULES_TABLE = 'tddc_pc_rules'
    RULES_FAMILY = 'rules'
    RULES_QUALIFIER = 'index'
    
    # Proxy Checker Event Topic Info
    EVENT_TOPIC = 'tddc_pc_event'
    EVENT_TOPIC_GROUP = 'tddc.pc.{mac}.{id}'.format(mac=get_mac_address(),
                                                    id=CLIENT_ID)
    
    # Proxy Checker Task Topic Info
    TOPIC_GROUP = 'tddc.pc.parser'
    
    # Proxy Checker Concurrent
    CONCURRENT = 16
    
    # Source Proxy Set Key
    HTTP_SOURCE_PROXY_SET_KEY = 'tddc:test:proxy:ip_src:http'
    HTTPS_SOURCE_PROXY_SET_KEY = 'tddc:test:proxy:ip_src:https'
