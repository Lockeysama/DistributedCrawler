# -*- coding: utf-8 -*-
'''
Created on 2017年5月8日

@author: chenyitao
'''
import logging

from ..util.util import Singleton
from ..redis.redis_client import RedisClient

from .models import DBSession, RedisModel

log = logging.getLogger(__name__)


class CacheManager(RedisClient):
    '''
    classdocs
    '''
    __metaclass__ = Singleton

    def __init__(self):
        nodes = DBSession.query(RedisModel).all()
        if not nodes:
            log.warning('>>> Redis Nodes Not Found.')
            return
        nodes = [{'host': node.host,
                  'port': node.port} for node in nodes]
        super(CacheManager, self).__init__(startup_nodes=nodes)
        log.info('Cache Manager Was Ready.')

    def get_random(self, name, pop=True):
        def _get_random(_name, _pop):
            if _pop:
                return self.spop(_name)
            return self.srandmember(_name)
        return self.robust(_get_random, name, pop)

    def set(self, name, *cache):
        def _set(_name, *_cache):
            self.sadd(_name, *_cache)
        self.robust(_set, name, *cache)

    def remove(self, name, *cache):
        def _remove(_name, *_cache):
            self.srem(_name, *_cache)
        self.robust(_remove, name, *cache)
