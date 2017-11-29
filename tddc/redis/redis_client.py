# -*- coding: utf-8 -*-
'''
Created on 2017年4月10日

@author: chenyitao
'''

import gevent
from rediscluster import StrictRedisCluster

from ..log.logger import TDDCLogger


class RedisClient(StrictRedisCluster, TDDCLogger):
    '''
    classdocs
    '''

    def smadd(self, name, values):
        '''
        批量sadd
        '''
        ppl = self.pipeline()
        for value in values:
            ppl.sadd(name, value)
        return ppl.execute()

    def smpop(self, name, count):
        '''
        批量spop
        '''
        ppl = self.pipeline()
        for _ in range(count):
            ppl.spop(name)
        return ppl.execute()

    def hmdel(self, name, values):
        '''
        批量hdel
        '''
        ppl = self.pipeline()
        for value in values:
            ppl.hdel(name, value)
        return ppl.execute()

    def hmove(self, old_name, new_name, key, value):
        ppl = self.pipeline()
        if old_name:
            ppl.hdel(old_name, key)
        ppl.hset(new_name, key, value)
        return ppl.execute()

    def happend(self, name, key, tag, new_status):
        status = self.get_status(name, key)
        status = status.split('|')
        status.append('%s_%d' % (tag, new_status))
        new = '|'.join(status)
        self.hset(name, key, new)

    def psubscribe(self, pattern):
        '''
        匹配订阅
        '''
        ps = self.pubsub()
        ps.psubscribe(pattern)
        self.logger.info('Subscribe %s...' % pattern)
        for item in ps.listen():
            yield item
        ps.unsubscribe('spub')
        self.logger.warning('Subscribe Was Exit.')

    @staticmethod
    def timer(seconds, callback, *args, **kwargs):
        def _timer(_callback, *_args, **_kwargs):
            callback(*_args, **_kwargs)

        gevent.spawn_later(seconds, _timer, callback, *args, **kwargs)
        gevent.sleep()
