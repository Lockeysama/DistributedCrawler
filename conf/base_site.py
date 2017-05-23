# -*- coding: utf-8 -*-
'''
Created on 2017年4月12日

@author: chenyitao
'''

from enum import Enum

from .default import *

Worker = Enum('Worker', ('Crawler', 'Parser', 'ProxyChecker', 'Monitor'))

class BaseSite(CookiesSite,
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

    # Platform Suffix
    PLATFORM_SUFFIX = '_test' if TEST else ''
   
    # Current Worker
    WORKER = Worker.Crawler
#     WORKER = Worker.Parser
#     WORKER = Worker.ProxyChecker
#     WORKER = Worker.Monitor
