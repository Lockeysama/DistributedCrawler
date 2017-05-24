# -*- coding: utf-8 -*-
'''
Created on 2017年5月24日

@author: chenyitao
'''

import copy
import json

class QuickModelBase(object):
    '''
    classdocs
    '''

    default_values = {}

    def __init__(self, **kwargs):
        self.__dict__ = copy.copy(self.default_values)
        for key in self.__dict__:
            if key in kwargs:
                self.__dict__[key] = kwargs.pop(key)

    def __repr__(self, *args, **kwargs):
        return self.to_json()

    def to_dict(self):
        return {k:v if not isinstance(v, list) else [sub.to_dict() if isinstance(sub, QuickModelBase) else sub 
                                                     for sub in v] 
                for k,v in self.__dict__.items() 
                if v != None}

    def to_json(self):
        return json.dumps(self.to_dict())
