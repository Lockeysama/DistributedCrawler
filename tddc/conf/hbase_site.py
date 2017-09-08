# -*- coding: utf-8 -*-
'''
Created on 2017年5月23日

@author: chenyitao
'''

import random
from tddc.conf.server import HOST


class HBaseSite(object):

    HBASE_NODES = [HOST + ':9090']
    
    @staticmethod
    def random_hbase_node():
        return random.choice(HBaseSite.HBASE_NODES)
