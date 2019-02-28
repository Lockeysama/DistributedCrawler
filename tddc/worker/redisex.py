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
import time
from os import getpid

import gevent
import six

from ..base.util import Singleton
from ..base.redis import RedisClient
from ..default_config import default_config

log = logging.getLogger(__name__)


@six.add_metaclass(Singleton)
class RedisEx(RedisClient):
    """
    消息队列
    """

    def __init__(self, nodes=None, tag='default'):
        super(RedisEx, self).__init__(startup_nodes=nodes or self.nodes(tag))

    def nodes(self, tag):
        from .online_config import OnlineConfig
        node = getattr(OnlineConfig().redis, tag)
        if not node:
            return []
        return [node]

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

    def get_records(self, name):
        """
        获取任务记录
        :param name: 任务索引
        :return:
        """
        def _get_record(_name):
            return self.hgetall(_name)

        record = self.robust(_get_record, name)
        return record

    def subscribing(self):
        def _subscribing():
            topic = self._subscribe_topic()
            if not topic:
                log.warning('Subscribe Topic Is None.')
                return
            log.info('Subscribing: %s' % topic)
            p = self.pubsub()
            p.subscribe(topic)
            for item in p.listen():
                if default_config.PID != getpid():
                    return
                if item.get('type') == 'message':
                    data = item.get('data')
                    try:
                        self._data_fetched(data)
                    except Exception as e:
                        log.warning(e)
            p.unsubscribe(topic)

        while True:
            if default_config.PID != getpid():
                return
            try:
                self.robust(_subscribing)
            except Exception as e:
                log.warning(e)
            gevent.sleep(5)

    def _subscribe_topic(self):
        """
        返回订阅的topic
        """
        pass

    def _data_fetched(self, data):
        """
        解析接收到订阅的内容
        :param data:
        """
        pass

    def publish_robust(self, channel, message):
        def _publish(_channel, _message):
            self.publish(_channel, _message)
        self.robust(_publish, channel, message)
