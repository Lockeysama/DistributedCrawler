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
from tddc.base.util import Singleton
from ...base.redisex_for_manager import RedisExForManager

from .models import ProxyTask

log = logging.getLogger(__name__)


@six.add_metaclass(Singleton)
class ProxyHelper(object):

    key_base = 'tddc:worker:config:common:proxy_check_list'

    def edit(self, proxy_task):
        RedisExForManager().hmset(
            '{}:{}'.format(self.key_base, proxy_task.s_feature),
            proxy_task.to_dict()
        )

    def delete(self, feature):
        RedisExForManager().delete(
            '{}:{}'.format(self.key_base, feature)
        )

    def query(self, feature='*'):
        if feature == '*':
            keys = RedisExForManager().keys('{}:*'.format(self.key_base))
            return [ProxyTask(**RedisExForManager().hgetall(key)) for key in keys]
        else:
            key = RedisExForManager().keys('{}:{}'.format(
                self.key_base, feature)
            )
            if key:
                key = key[0]
            return ProxyTask(**RedisExForManager().hgetall(key))
