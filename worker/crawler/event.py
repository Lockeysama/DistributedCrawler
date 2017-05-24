# -*- coding: utf-8 -*-
'''
Created on 2017年5月24日

@author: chenyitao
'''

from conf import CrawlerSite
from common import singleton
from ..base import EventManagreBase


@singleton
class CrawlerEventCenter(EventManagreBase):
    '''
    classdocs
    '''

    NODES = CrawlerSite.KAFKA_NODES
    
    TOPIC = CrawlerSite.EVENT_TOPIC
    
    GROUP = CrawlerSite.EVENT_TOPIC_GROUP

        
def main():
    pass

if __name__ == '__main__':
    main()
