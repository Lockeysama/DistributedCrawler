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
import setproctitle

import logging

from ..default_config import default_config
from ..base.util import Device, Singleton

from redisex import RedisEx

log = logging.getLogger(__name__)


class Authorization(RedisEx):

    __metaclass__ = Singleton

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
            'ip': Device.ip(),
            'mac': Device.mac(),
            'platform': default_config.PLATFORM,
            'feature': default_config.FEATURE,
            'pid': os.getpid(),
            'process_title': setproctitle.getproctitle()
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
                    self.register_info.get('ip'),
                    self.register_info.get('platform'),
                    self.register_info.get('pid')
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
