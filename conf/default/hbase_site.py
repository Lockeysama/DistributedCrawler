# -*- coding: utf-8 -*-
'''
Created on 2017年5月23日

@author: chenyitao
'''

import random


class HBaseSite(object):

    HBASE_NODES = ['72.127.2.48:9090']
#     HBASE_NODES = ['192.168.1.108:9090']
    
    @staticmethod
    def random_hbase_node():
        return random.choice(HBaseSite.HBASE_NODES)
