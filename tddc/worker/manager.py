# -*- coding: utf-8 -*-
'''
Created on 2017年6月12日

@author: chenyitao
'''

from ..log.logger import TDDCLogger
from ..event.event import EventCenter
from ..exception.exception import ExceptionCollection
from .extern_modules.extern_manager import ExternManager


class WorkerManager(TDDCLogger):
    '''
    classdocs
    '''

    def __init__(self):
        super(WorkerManager, self).__init__()
        EventCenter()
        ExceptionCollection()
        ExternManager()

    @staticmethod
    def start():
        pass
