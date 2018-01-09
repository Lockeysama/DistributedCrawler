# -*- coding: utf-8 -*-
'''
Created on 2017年5月8日

@author: chenyitao
'''

import time

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
            print('>>> Redis Nodes Not Found.')
            return
        nodes = [{'host': node.host,
                  'port': node.port} for node in nodes]
        super(StatusManager, self).__init__(startup_nodes=nodes)
        self.info('Status Manager Was Ready.')

    def get_status(self, name, key):
        def _get_status(_name, _key):
            return self.hget(_name, _key)
        return self.robust(_get_status, name, key)

    def update_status(self, name, key, new_status, old_status=None):
        def _update_status(_name, _key, _new_status, _old_status):
            self.hmove((_name + ':' + str(_old_status)) if _old_status is not None else None,
                       _name + ':' + str(_new_status),
                       _key,
                       str(int(time.time())))
        self.robust(_update_status, name, key, new_status, old_status)

    def set_status(self, name, key, status):
        def _set_status(_name, _key, _status):
            self.hset(_name, key, _status)
        self.robust(_set_status, name, key, status)

    def set_multi_status(self, name, status):
        def _set_multi_status(_name, _status):
            self.hmset(_name, _status)
        self.robust(_set_multi_status, name, status)

    def get_all_status(self, name):
        def _get_all_status(_name):
            return self.hscan_iter(_name)
        return self.robust(_get_all_status, name)
