# -*- coding: utf-8 -*-
"""
@author  : chenyitao
@email   : yt.chen@bshier.com
@license: Apache Licence
@software: PyCharm
@file    : publish.py
@time    : 2018/9/10 12:03
"""
import logging

from ..util.util import Singleton
from ..redis.redis_client import RedisClient

from .models import RedisModel, DBSession

log = logging.getLogger(__name__)


class Publish(RedisClient):
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
        super(Publish, self).__init__(startup_nodes=nodes)

    def publish_robust(self, channel, message):
        def _publish(_channel, _message):
            self.publish(_channel, _message)
        self.robust(_publish, channel, message)
