# -*- coding: utf-8 -*-
'''
Created on 2017年4月10日

@author: chenyitao
'''

from rediscluster import StrictRedisCluster


class RedisClient(object):
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
        self._rdm = StrictRedisCluster(startup_nodes=self._nodes, decode_responses=True)
        
    def __del__(self):
        self._rdm.client.close()


class RepeatFilter(object):
    
    def __init__(self, redis_client):
        self._rdm = redis_client._rdm
    
    def get_repeats(self, name, items):
        repeat = None
        for item in items:
            if not self._rdm.sadd(name, item):
                if not repeat:
                    repeat = set()
                repeat.add(item)
        return repeat


class URLFilter(RepeatFilter):
    pass


def main():
    import time
    nodes = [{'host': '72.127.2.48', 'port': '7000'},
             {'host': '72.127.2.48', 'port': '7001'},
             {'host': '72.127.2.48', 'port': '7002'},
             {'host': '72.127.2.48', 'port': '7003'},
             {'host': '72.127.2.48', 'port': '7004'},
             {'host': '72.127.2.48', 'port': '7005'}]
    client = RedisClient(nodes=nodes)
    
    items = set([i for i in range(43)])
    url_filter = URLFilter(client)
    repeat = url_filter.get_repeats('stest', items)
    print(repeat)
    if repeat:
        print(items ^ repeat)
    else:
        print('No repeat item')
    while True:
        time.sleep(1)

if __name__ == '__main__':
    main()