# encoding: utf-8
"""
@version: ??
@author: chenyitao
@license: Apache Licence 
@software: PyCharm
@file: config.py
@time: 2018/3/19 11:04
"""

import os

from tddc.default_config import default_config

basedir = os.path.abspath(os.path.dirname(__file__))


default_config.PLATFORM = 'API-Server'


default_config.DEFAULT_REDIS_NODES = [
    {'host': '127.0.0.1', 'port': 6379, 'password': None}
]
