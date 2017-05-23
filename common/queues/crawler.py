# -*- coding: utf-8 -*-
'''
Created on 2017年5月22日

@author: chenyitao
'''

from gevent.queue import Queue
from .public import PublicQueues


class CrawlerQueues(PublicQueues):
    ## Crawler
    # Task Base Info Update Queue
    TASK_BASE_INFO_UPDATE = Queue()
    # Proxy IP Platform Queue 
    PROXY_IP_PLATFORM = Queue()
    # Platform Proxy Queues
    PLATFORM_PROXY = dict()
    # Platform Cookies Queues
    PLATFORM_COOKIES = dict()
    # Unuseful Proxy Feedback Queue
    UNUSEFUL_PROXY_FEEDBACK = Queue()
