# -*- coding: utf-8 -*-
'''
Created on 2017年5月23日

@author: chenyitao
'''

from tddc.conf.server import HOST


class ZookeeperSite(object):

    ZK_NODES = [HOST + ':2181']
