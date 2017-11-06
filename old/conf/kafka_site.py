# -*- coding: utf-8 -*-
'''
Created on 2017年5月23日

@author: chenyitao
'''

from old import HOST

class KafkaSite(object):

    KAFKA_NODES = ','.join([HOST + ':9092'])
