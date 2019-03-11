# -*- coding: utf-8 -*-
"""
Created on 2017年8月31日

@author: chenyitao
"""
from tddc.default_config import default_config

from tddc.worker import ProxiesChecker

default_config.PLATFORM = 'Proxy'

default_config.DEFAULT_REDIS_NODES = [
    {'host': '127.0.0.1', 'port': 6379, 'password': None}
]

ProxiesChecker.HTTP_CHECK_CONCURRENT = 32

ProxiesChecker.HTTPS_CHECK_CONCURRENT = 32
