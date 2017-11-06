# -*- coding: utf-8 -*-
'''
Created on 2017年9月6日

@author: chenyitao
'''

from .cookies_site import CookiesSite
from .event_site import EventSite
from .exception_site import ExceptionSite
from .hbase_site import HBaseSite
from .kafka_site import KafkaSite
from .proxy_site import ProxySite
from .redis_site import RedisSite
from .task_site import TaskSite
from .zookeeper_site import ZookeeperSite


def get_mac_address():
    import uuid
    mac=uuid.UUID(int = uuid.getnode()).hex[-12:] 
    return ":".join([mac[e:e+2] for e in range(0,11,2)])


class SiteBase(CookiesSite,
               EventSite,
               ExceptionSite,
               HBaseSite,
               KafkaSite,
               ProxySite,
               RedisSite,
               TaskSite,
               ZookeeperSite):

    # Test
    TEST = True
    
    # Client ID
    CLIENT_ID = 1

    CONF_DB_PATH = './conf.db'
    
    WORKER_NAME = 'TDDC_Worker'
   
    PLATFORM_CONF_TABLE = 'tddc_platform_conf_table' 

    EVENT_TOPIC_GROUP = 'tddc.pc.{mac}.{id}'.format(mac=get_mac_address(),
                                                    id=CLIENT_ID) 
