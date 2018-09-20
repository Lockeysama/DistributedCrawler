# -*- coding: utf-8 -*-
"""
@author  : chenyitao
@email   : yt.chen@bshier.com
@license: Apache Licence
@software: PyCharm
@file    : RedisEx.py
@time    : 2018/9/18 15:10
"""
import logging

from ..util.util import Singleton
from ..redis.redis_client import RedisClient

from .online_config import OnlineConfig

log = logging.getLogger(__name__)


class RedisEx(RedisClient):
    """
    消息队列
    """
    __metaclass__ = Singleton

    def __init__(self, nodes=None, tag='default'):
        super(RedisEx, self).__init__(startup_nodes=nodes or self.nodes())

    def nodes(self):
        nodes = [{'host': node.get('host'),
                  'port': node.get('port')}
                 for node in OnlineConfig().redis if node.get('default')]
        return nodes

    def push(self, topic, values, callback=None):
        def _push(_topic, _values, _callback):
            self.lpush(_topic, _values)
            if _callback:
                _callback((_topic, _values))
        self.robust(_push, topic, values, callback)

    def pull(self, topic, count=0, timeout=2):
        count = int(count)

        def _pull(_topic, _count, _timeout):
            if count == 0:
                return self.brpop(_topic, timeout)
            cnt = self.llen(_topic)
            cnt = _count if cnt > _count else cnt
            if cnt == 0:
                return None
            with self.pipeline() as ppl:
                for _ in range(cnt):
                    ppl.brpop(_topic, 1)
                ret = ppl.execute()
                ret = [data for data in ret if data]
                return [data for _, data in ret]
        return self.robust(_pull, topic, count, timeout)

    def create_records(self, name, records):
        def _create_records(_name, _records):
            if not _name and isinstance(_records, list):
                with self.pipeline(transaction=False) as ppl:
                    for key, _record in _records:
                        ppl.hmset(key, _record)
                    ret = ppl.execute()
                return ret
            else:
                self.hmset(_name, _records)
        if not records:
            return None
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


