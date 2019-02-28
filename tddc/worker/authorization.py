# -*- coding: utf-8 -*-
"""
@author  : chenyitao
@email   : yt.chen@bshier.com
@license: Apache Licence
@software: PyCharm
@file    : register.py
@time    : 2018/9/10 17:53
"""
import json
import os

import logging
import time

import six

from ..default_config import default_config
from ..base.util import Device, Singleton

from .redisex import RedisEx

log = logging.getLogger(__name__)


@six.add_metaclass(Singleton)
class Authorization(RedisEx):

    _register_info = {}

    def __init__(self):
        super(Authorization, self).__init__()
        self.register()
        self.logged = self.login()

    def nodes(self, tag):
        return default_config.DEFAULT_REDIS_NODES

    @property
    def register_info(self):
        if self._register_info:
            return self._register_info
        self._register_info = {
            's_ip': Device.ip(),
            's_mac': Device.mac(),
            's_platform': default_config.PLATFORM,
            'i_pid': os.getpid(),
            'i_date': int(time.time())
        }
        return self._register_info

    def register(self):
        self.push('tddc:worker:register', json.dumps(self.register_info))
        log.info('In The Register.')

    def login(self):
        log.info('Waiting For Authorization.')
        while True:
            result = self.pull(
                topic='tddc:worker:register:pass:{}:{}:{}'.format(
                    self.register_info.get('s_ip'),
                    self.register_info.get('s_platform'),
                    self.register_info.get('i_pid')
                ),
                timeout=5
            )
            if result:
                result = json.loads(result[1])
                if result.get('code') == 0:
                    log.info('Authorization Success.')
                    return True
                else:
                    log.info('Authorization Failed().'.format(result))
                    return False
