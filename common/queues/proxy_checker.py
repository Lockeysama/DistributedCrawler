# -*- coding: utf-8 -*-
'''
Created on 2017年5月22日

@author: chenyitao
'''

from gevent.queue import Queue
from .public import PublicQueues


class ProxyCheckerQueues(PublicQueues):
    ## Proxy Checker
    # Useful Proxy Queue
    USEFUL_PROXY = Queue()
    # Source Proxy Queue
    HTTP_SOURCE_PROXY = Queue()
    HTTPS_SOURCE_PROXY = Queue()
