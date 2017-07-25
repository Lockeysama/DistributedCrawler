# -*- coding: utf-8 -*-
'''
Created on 2017年4月10日

@author: chenyitao
'''

from rediscluster import StrictRedisCluster
from common import TDDCLogging


class RedisClient(StrictRedisCluster):
    '''
    classdocs
    '''

    def __init__(self, nodes=None):
        '''
        Constructor
        '''
        self._nodes = nodes
        if not self._nodes:
            self._nodes = [{'host': 'localhost', 'port': '6281'}]
        super(RedisClient, self).__init__(startup_nodes=self._nodes,
                                          decode_responses=True)

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
        for _ in xrange(count):
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

    def psubscribe(self, pattern):
        '''
        匹配订阅
        '''
        ps = self.pubsub()
        ps.psubscribe(pattern)
        TDDCLogging.info('--->Pubsub Was Ready.')
        for item in ps.listen():
            yield item
        ps.unsubscribe('spub')
        TDDCLogging.info('-->Pubsub Is Exit.')


def main():
    pass

if __name__ == '__main__':
    main()