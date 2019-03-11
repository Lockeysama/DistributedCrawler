# -*- coding: utf-8 -*-
"""
@author  : chenyitao
@email   : yt.chen@bshier.com
@license: Apache Licence
@software: PyCharm
@file    : helper.py
@time    : 2018/10/24 16:47
"""
import logging

import six
from ......base.util import Singleton
from ......worker.redisex import RedisEx

from .models import ProxyTask

log = logging.getLogger(__name__)


@six.add_metaclass(Singleton)
class ProxyHelper(object):

    key_base = 'tddc:worker:config:common:proxy_check_list'

    def edit(self, proxy_task):
        RedisEx().hmset(
            '{}:{}'.format(self.key_base, proxy_task.s_feature),
            proxy_task.to_dict()
        )

    def delete(self, feature):
        RedisEx().delete(
            '{}:{}'.format(self.key_base, feature)
        )

    def query(self, feature='*'):
        if feature == '*':
            keys = RedisEx().keys('{}:*'.format(self.key_base))
            return [ProxyTask(**RedisEx().hgetall(key)) for key in keys]
        else:
            key = RedisEx().keys('{}:{}'.format(
                self.key_base, feature)
            )
            if key:
                key = key[0]
            return ProxyTask(**RedisEx().hgetall(key))
