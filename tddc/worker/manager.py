# -*- coding: utf-8 -*-
'''
Created on 2017年6月12日

@author: chenyitao
'''

from .extern_modules.extern_manager import ExternManager
from ..log.logger import TDDCLogger


class WorkerManager(TDDCLogger):
    '''
    classdocs
    '''

    def __init__(self):
        super(WorkerManager, self).__init__()
        ExternManager()

    @staticmethod
    def start():
        pass
