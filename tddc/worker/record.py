# -*- coding: utf-8 -*-
'''
Created on 2017年5月8日

@author: chenyitao
'''

import gevent

from ..util.util import Singleton
from ..redis.redis_client import RedisClient

from .worker_config import WorkerConfigCenter


class RecordManager(RedisClient):
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

    def create_record(self, name, key, record):
        times = 0
        while True:
            try:
                self.hset(name, key, record)
            except Exception as e:
                self.exception(e)
                gevent.sleep(1)
                times += 1
                if times == 5:
                    self.error('Create Record [%s:%s:%s] Failed.'.format(name, key, record))
                    break
            else:
                break

    def get_record(self, name, key, callback, **kwargs):
        times = 0
        while True:
            try:
                record = self.hget(name, key)
            except Exception as e:
                self.exception(e)
                gevent.sleep(0.5)
                times += 1
                if times == 5:
                    self.error('Get Record [%s:%s] Failed.'.format(name, key))
                    break
            else:
                callback(record, **kwargs)
                break
