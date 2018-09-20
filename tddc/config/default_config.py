# -*- coding: utf-8 -*-
"""
@author  : chenyitao
@email   : yt.chen@bshier.com
@license: Apache Licence
@software: PyCharm
@file    : default_config.py
@time    : 2018/9/11 10:38
"""
import os

PLATFORM = 'Test'

FEATURE = 'Test'

AUTH_REDIS_NODES = [{'host': '127.0.0.1', 'port': 6379, 'password': None}]

ONLINE_CONFIG_REDIS_NODES = [{'host': '127.0.0.1', 'port': 6379, 'password': None}]

REDIS_NODES = [{'host': '127.0.0.1', 'port': 6379, 'password': None}]

PID = os.getpid()
