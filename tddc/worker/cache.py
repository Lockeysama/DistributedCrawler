# -*- coding: utf-8 -*-
'''
Created on 2017年5月8日

@author: chenyitao
'''

from ..util.util import Singleton
from ..redis.redis_client import RedisClient

from .worker_config import WorkerConfigCenter


class CacheManager(RedisClient):
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

    def get_random(self, name, pop=True):
        if pop:
            return self.spop(name)
        return self.srandmember(name)

    def set(self, name, *cache):
        self.sadd(name, *cache)

    def remove(self, name, *cache):
        self.srem(name, *cache)
