# -*- coding: utf-8 -*-
'''
Created on 2017年5月8日

@author: chenyitao
'''

from .redis_client import RedisClient


class CacheManager(RedisClient):
    '''
    classdocs
    '''

    def get_random(self, name, pop=True):
        if pop:
            return self.spop(name)
        return self.srandmember(name)

    def set(self, name, *cache):
        self.sadd(name, *cache)

    def remove(self, name, *cache):
        self.srem(name, *cache)
