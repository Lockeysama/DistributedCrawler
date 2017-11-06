# -*- coding: utf-8 -*-
'''
Created on 2017年6月12日

@author: chenyitao
'''

from ..event.event import EventCenter
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
        PackagesManager().start(site.CONF_DB_PATH, site)
        ExceptionCollection().start(site.KAFKA_NODES)
        EventCenter().start(site)

    @staticmethod
    def start():
        pass
