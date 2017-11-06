# -*- coding: utf-8 -*-
'''
Created on 2017年5月23日

@author: chenyitao
'''

from old import HOST


class RedisSite():
    
    # Redis Info

    REDIS_NODES = [{'host': HOST, 'port': '7000'},
                   {'host': HOST, 'port': '7001'},
                   {'host': HOST, 'port': '7002'},
                   {'host': HOST, 'port': '7003'},
                   {'host': HOST, 'port': '7004'},
                   {'host': HOST, 'port': '7005'}]

