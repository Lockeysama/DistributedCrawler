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

    @staticmethod
    def members():
        return {}
    
    @staticmethod
    def types():
        return {}

    def __init__(self, **kwargs):
        self.__dict__ = copy.copy(self.members())
        for key in self.__dict__:
            if key not in kwargs:
                continue
            if key not in self.types():
                self.__dict__[key] = kwargs.pop(key)
            else:
                self._init_special_type(key, **kwargs)

    def _init_special_type(self, key, **kwargs):
        cls = self.types().get(key)
        if not cls:
            return
        if isinstance(cls, list) and issubclass(cls[0], QuickModelBase):
            for info in kwargs.pop(key):
                if not self.__dict__.get(key):
                    self.__dict__[key] = []
                self.__dict__[key].append(cls[0](**info))
        elif issubclass(cls, QuickModelBase):
            self.__dict__[key] = cls(**kwargs.pop(key))
        else:
            self.__dict__[key] = kwargs.pop(key)

    def __repr__(self, *args, **kwargs):
        return self.to_json()

    def to_dict(self):
        kvs = {}
        for k,v in self.__dict__.items():
            if not isinstance(v, list) and not isinstance(v, QuickModelBase):
                kvs[k] = v
            else:
                self.special_to_dict(kvs, k, v)
        return kvs

    @staticmethod
    def special_to_dict(kvs, k, v):
        if isinstance(v, QuickModelBase):
            kvs[k] = v.to_dict()
        elif isinstance(v, list) and not len(v):
            kvs[k] = v
        else:
            if isinstance(v[0], QuickModelBase):
                kvs[k] = [sub.to_dict() for sub in v]
            else:
                kvs[k] = v

    def to_json(self):
        return json.dumps(self.to_dict(), indent=1)
