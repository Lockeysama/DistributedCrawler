# -*- coding: utf-8 -*-
"""
@author  : chenyitao
@email   : yt.chen@bshier.com
@license: Apache Licence
@software: PyCharm
@file    : mq.py
@time    : 2018/9/11 17:11
"""
import logging

from ..util.util import Singleton
from ..redis.redis_client import RedisClient

log = logging.getLogger(__name__)


class MQ(RedisClient):
    """
    消息队列
    """
    __metaclass__ = Singleton

    def __init__(self):
        super(MQ, self).__init__(startup_nodes=self.nodes())

    def nodes(self):
        raise NotImplementedError

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
