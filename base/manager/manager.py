# -*- coding: utf-8 -*-
'''
Created on 2017年6月12日

@author: chenyitao
'''

import setproctitle

import settings
from ..exception.exception import ExceptionCollection
from ..event.event import EventCenter


class WorkerManager(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        setproctitle.setproctitle('TDDC_' + settings.WORKER.name)  # @UndefinedVariable
        ExceptionCollection()
        EventCenter()

    @staticmethod
    def start():
        pass
