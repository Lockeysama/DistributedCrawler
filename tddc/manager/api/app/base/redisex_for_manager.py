# -*- coding: utf-8 -*-
"""
@author  : chenyitao
@email   : yt.chen@bshier.com
@license: Apache Licence
@software: PyCharm
@file    : redisex_for_manager.py
@time    : 2018/10/23 17:28
"""
from tddc.default_config import default_config
from tddc.worker import RedisEx


class RedisExForManager(RedisEx):

    def nodes(self, tag):
        return default_config.DEFAULT_REDIS_NODES
