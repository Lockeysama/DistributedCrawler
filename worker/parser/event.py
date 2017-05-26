# -*- coding: utf-8 -*-
'''
Created on 2017年5月24日

@author: chenyitao
'''

from conf import ParserSite
from common import singleton
from ..base import EventManagreBase


@singleton
class ParserEventCenter(EventManagreBase):
    '''
    classdocs
    '''

    NODES = ParserSite.KAFKA_NODES
    
    TOPIC = ParserSite.EVENT_TOPIC
    
    GROUP = ParserSite.EVENT_TOPIC_GROUP
