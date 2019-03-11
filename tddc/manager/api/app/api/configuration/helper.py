# encoding: utf-8
"""
@version: ??
@author: chenyitao
@license: Apache Licence 
@software: PyCharm
@file: helper.py
@time: 2019-02-13 14:51
"""
import logging

import six
from tddc.base.util import Singleton

from ......worker.redisex import RedisEx


log = logging.getLogger(__name__)


@six.add_metaclass(Singleton)
class ConfigsHelper(object):

    key_base = 'tddc:worker:config'

    def edit(self, path, config):
        _path = '{}:{}'.format(self.key_base, ':'.join(path))
        for k1, v1 in config.items():
            for k2, v2 in v1.items():
                for k3, v3 in v2.items():
                    RedisEx().hset('{}:{}:{}'.format(_path, k1, k2), k3, v3)
        return True

    def delete(self, path, config):
        _path = '{}:{}'.format(self.key_base, ':'.join(path))
        for k1, v1 in config.items():
            if v1 == '*':
                RedisEx().clean('{}:{}:*'.format(_path, k1))
                return True
            for k2, v2 in v1.items():
                if v2 == '*':
                    RedisEx().clean('{}:{}:{}'.format(_path, k1, k2))
                    return True
                for k3, _ in v2.items():
                    RedisEx().hdel('{}:{}:{}'.format(_path, k1, k2), k3)
        return True
