# -*- coding: utf-8 -*-
'''
Created on 2017年5月8日

@author: chenyitao
'''

import time

import gevent

from tddc.config.config_center import ConfigCenter
from tddc.util import Singleton
from .redis_client import RedisClient


class StatusManager(RedisClient):
    '''
    classdocs
    '''

    def get_status(self, name, key):
        times = 0
        while True:
            try:
                value = self.hget(name, key)
            except Exception, e:
                self.logger.warning(e)
                gevent.sleep(0.5)
                times += 1
                if times == 5:
                    self.logger.error('Get Status [%s:%s] Failed.'.format(name, key))
                    break
            else:
                break
        return value

    def update_status(self, name, key, new_status, old_status=None):
        times = 0
        while True:
            try:
                self.hmove((name + str(old_status)) if old_status else None,
                           name + str(new_status),
                           key,
                           str(int(time.time())))
            except Exception, e:
                self.logger.warning(e)
                gevent.sleep(0.5)
                times += 1
                if times == 5:
                    self.logger.error('Update Status [%s:%s:%s] Failed.'.format(name, key, str(new_status)))
                    break
            else:
                break
