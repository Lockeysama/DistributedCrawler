# -*- coding: utf-8 -*-
'''
Created on 2017年5月8日

@author: chenyitao
'''

import time

import gevent

from ..util.util import Singleton
from ..redis.redis_client import RedisClient

from .worker_config import WorkerConfigCenter


class StatusManager(RedisClient):
    '''
    classdocs
    '''
    __metaclass__ = Singleton

    def __init__(self):
        nodes = WorkerConfigCenter().get_redis()
        if not nodes:
            return
        nodes = [{'host': node.host,
                  'port': node.port} for node in nodes]
        super(RedisClient, self).__init__(startup_nodes=nodes)

    def get_status(self, name, key):
        times = 0
        value = None
        while True:
            try:
                value = self.hget(name, key)
            except Exception as e:
                self.exception(e)
                gevent.sleep(0.5)
                times += 1
                if times == 5:
                    self.error('Get Status [%s:%s] Failed.'.format(name, key))
                    break
            else:
                break
        return value

    def update_status(self, name, key, new_status, old_status=None):
        times = 0
        while True:
            try:
                self.hmove((name + ':' + str(old_status)) if old_status is not None else None,
                           name + ':' + str(new_status),
                           key,
                           str(int(time.time())))
            except Exception as e:
                self.exception(e)
                gevent.sleep(0.5)
                times += 1
                if times == 5:
                    self.error('Update Status [%s:%s:%s] Failed.'.format(name, key, str(new_status)))
                    break
            else:
                break

    def append_status(self, name, key, tag, new_status):
        times = 0
        while True:
            try:
                self.happend(name, key, tag, new_status)
            except Exception as e:
                self.exception(e)
                gevent.sleep(0.5)
                times += 1
                if times == 5:
                    self.error('Update Status [%s:%s:%s] Failed.'.format(name, key, str(new_status)))
                    break
            else:
                break
