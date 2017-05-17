# -*- coding: utf-8 -*-
'''
Created on 2017年5月16日

@author: chenyitao
'''

import hashlib
from plugins import RedisClient
from conf.base_site import REDIS_NODES


class SimpleHash(object):
    '''
    classdocs
    '''

    def __init__(self, cap, seed):
        '''
        Constructor
        '''
        self.cap = cap
        self.seed = seed

    def hash(self, value):
        ret = 0
        for i in range(len(value)):
            ret += self.seed * ret + ord(value[i])
        return (self.cap - 1) & ret


class BloomFilter(object):
    
    def __init__(self, redis_cli=None):
        self.rdm = redis_cli
        if not redis_cli:
            self.rdm = RedisClient(REDIS_NODES)._rdm
        self.bit_size = 1 << 31
        self.seeds = [5, 7, 11, 13, 31, 37, 61]
        self.key = 'bloomfilter_test'
        self.block_num = 1
        self.hash_func = [SimpleHash(self.bit_size, seed) for seed in self.seeds]
        
    def is_contains(self, value):
        if not value:
            return False
        md5 = hashlib.md5()
        md5.update(value)
        md5_value = md5.hexdigest()
        ret = True
        name = self.key + str(int(md5_value[0:2], 16) % self.block_num)
        for f in self.hash_func:
            loc = f.hash(md5_value)
            ret = ret & self.rdm.getbit(name, loc)
        return ret

    def insert(self, value):
        md5 = hashlib.md5()
        md5.update(value)
        md5_value = md5.hexdigest()
        name = self.key + str(int(md5_value[0:2], 16) % self.block_num)
        for f in self.hash_func:
            loc = f.hash(md5_value)
            self.rdm.setbit(name , loc, 1)
            
    def setget(self, value):
        if self.is_contains(value):
            return 0
        self.insert(value)
        return 1
        
        
def main():
    import time
    bf = BloomFilter()
    print(time.clock())
    for i in range(1000):
        print(bf.setget('http:cyt.com/%d' % i))
    print(time.clock())

if __name__ == '__main__':
    main()
