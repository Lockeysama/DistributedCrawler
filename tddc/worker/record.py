# -*- coding: utf-8 -*-
'''
Created on 2017年5月8日

@author: chenyitao
'''
import logging

from ..util.util import Singleton
from ..redis.redis_client import RedisClient

from .models import RedisModel, DBSession

log = logging.getLogger(__name__)


class RecordManager(RedisClient):
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
        super(RecordManager, self).__init__(startup_nodes=nodes)
        log.info('Record Manager Was Ready.')

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

    def set_record_item_value(self, key, field, value):
        def _set_record_item_value(_key, _field, _value):
            return self.hset(_key, _field, _value)
        return self.robust(_set_record_item_value, key, field, value)
