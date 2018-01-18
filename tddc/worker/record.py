# -*- coding: utf-8 -*-
'''
Created on 2017年5月8日

@author: chenyitao
'''

from ..util.util import Singleton
from ..redis.redis_client import RedisClient
from ..log.logger import TDDCLogger

from .worker_config import WorkerConfigCenter


class RecordManager(RedisClient):
    '''
    classdocs
    '''
    __metaclass__ = Singleton

    def __init__(self):
        nodes = WorkerConfigCenter().get_redis()
        if not nodes:
            TDDCLogger().warning('>>> Redis Nodes Not Found.')
            return
        nodes = [{'host': node.host,
                  'port': node.port} for node in nodes]
        super(RecordManager, self).__init__(startup_nodes=nodes)
        self.info('Status Manager Was Ready.')

    def create_record(self, name, key, record):
        def _create_record(_name, _key, _record):
            self.hset(_name, _key, _record)
        self.robust(_create_record, name, key, record)

    def create_records(self, name, records):
        def _create_records(_name, _records):
            self.hmset(_name, _records)
        self.robust(_create_records, name, records)

    def get_record_sync(self, name, key, callback, **kwargs):
        def _get_record_sync(_name, _key, _callback, **_kwargs):
            record = self.hget(_name, _key)
            _callback(record, **_kwargs)
        self.robust(_get_record_sync, name, key, callback, **kwargs)

    def get_record(self, name, key):
        def _get_record_sync(_name, _key):
            return self.hget(_name, _key)
        return self.robust(_get_record_sync, name, key)
