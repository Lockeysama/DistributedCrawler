# -*- coding: utf-8 -*-
'''
Created on 2017年5月8日

@author: chenyitao
'''
import logging
import gevent

from ..util.util import Singleton
from ..redis.redis_client import RedisClient

from .models import RedisModel, DBSession

log = logging.getLogger(__name__)


class Pubsub(RedisClient):
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
        super(Pubsub, self).__init__(startup_nodes=nodes)
        gevent.spawn(self.subscribing)
        gevent.sleep()

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
                if item.get('type') == 'message':
                    data = item.get('data')
                    self._data_fetched(data)
            p.unsubscribe(topic)
        self.robust(_subscribing)

    def _subscribe_topic(self):
        """
        返回订阅的topic
        """
        raise NotImplementedError

    def _data_fetched(self, data):
        """
        解析接收到订阅的内容
        :param data:
        """
        raise NotImplementedError

    def publish_robust(self, channel, message):
        def _publish(_channel, _message):
            self.publish(_channel, _message)
        self.robust(_publish, channel, message)
