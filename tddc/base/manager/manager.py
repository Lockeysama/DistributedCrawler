# -*- coding: utf-8 -*-
'''
Created on 2017年6月12日

@author: chenyitao
'''

from ..event.event import EventCenter, EventType
from ..exception.exception import ExceptionCollection
from ..package.packages_manager import PackagesManager


class WorkerManager(object):
    '''
    classdocs
    '''

    def __init__(self, site):
        '''
        Constructor
        '''
        PackagesManager().start(site.CONF_DB_PATH)
        ExceptionCollection().start(site.KAFKA_NODES)
        EventCenter().start(site.KAFKA_NODES,
                            site.EVENT_TOPIC,
                            site.EVENT_TOPIC_GROUP,
                            site.EVENT_TABLES)
        EventCenter().register(EventType.PACKAGES_UPDATE,
                               PackagesManager()._models_update_event)
    
    @staticmethod
    def start():
        pass
