# -*- coding: utf-8 -*-
"""
@author  : chenyitao
@email   : yt.chen@bshier.com
@license: Apache Licence
@software: PyCharm
@file    : register.py
@time    : 2018/9/10 17:53
"""
import os
import setproctitle

import logging

from ..config import default_config
from ..util.device_info import Device
from .message_queue import MessageQueue

log = logging.getLogger(__name__)


class Authorization(MessageQueue):

    def __init__(self):
        super(Authorization, self).__init__()
        self.register()
        self.login self.login()

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
        self.push('tddc:worker:register', self.register_info)
        log.info('In The Register.')

    def login(self):
        while True:
            result = self.pull(
                'tddc:worker:register:pass:{}:{}:{}'.format(
                    self.register_info.get('ip'),
                    self.register_info.get('platform'),
                    self.register_info.get('pid')
                ),
                5
            )
            if result:
                if result.get('code') == 0:
                    log.info('Register Success.')
                    return True
                else:
                    log.info('Register Failed().'.format(result))
                    return False
