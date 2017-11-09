# -*- coding: utf-8 -*-
'''
Created on 2017年5月5日

@author: chenyitao
'''

import json
import time


class Singleton(type):
    def __init__(cls, name, bases, dict):
        super(Singleton, cls).__init__(name, bases, dict)
        cls._instance = None

    def __call__(cls, *args, **kw):
        if cls._instance is None:
            cls._instance = super(Singleton, cls).__call__(*args, **kw)
        return cls._instance


def object2json(obj):
    info = {k: v for k, v in obj.__dict__.items()
            if v is not None
            and '__' not in k}
    return json.dumps(info)


def timer(func):
    '''
    执行时间计算装饰器
    '''
    def _deco(*args, **kwargs):
        start = time.time()
        func(*args, **kwargs)
        end = time.time()
        print(end-start)
    return _deco