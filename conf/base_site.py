# -*- coding: utf-8 -*-
'''
Created on 2017年4月12日

@author: chenyitao
'''

import uuid
from settings import Worker, WORKER, TEST, CLIENT_ID
from .default import *

def get_mac_address(): 
    mac=uuid.UUID(int = uuid.getnode()).hex[-12:] 
    return ":".join([mac[e:e+2] for e in range(0,11,2)])

class BaseSite(CookiesSite,
               EventSite,
               ExceptionSite,
               HBaseSite,
               KafkaSite,
               ProxySite,
               RedisSite,
               TaskSite,
               ZookeeperSite):

    # Platform Suffix
    PLATFORM_SUFFIX = '_test' if TEST else ''
   
    PLATFORM_CONF_TABLE = 'tddc_platform_conf_table' 

    # Proxy Checker Event Topic Info
    _EVENT_TOPICS = {Worker.Crawler: 'tddc_c_event',
                     Worker.Parser: 'tddc_p_event',
                     Worker.ProxyChecker: 'tddc_pc_event',
                     Worker.CookiesGenerator: 'tddc_cc_event',
                     Worker.Monitor: 'tddc_m_event',}
    
    EVENT_TOPIC = _EVENT_TOPICS[WORKER]
    EVENT_TOPIC_GROUP = 'tddc.pc.{mac}.{id}'.format(mac=get_mac_address(),
                                                    id=CLIENT_ID) 
