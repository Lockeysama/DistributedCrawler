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
import sys

PROJECT_ROOT = sys.path[0].split('/')[-1]

PLATFORM = 'Default'

FEATURE = 'Default' if len(sys.argv) < 2 else sys.argv[1]

DEFAULT_REDIS_NODES = [{'host': '127.0.0.1', 'port': 6379, 'password': None}]

PID = os.getpid()
