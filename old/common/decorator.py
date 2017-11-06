# -*- coding: utf-8 -*-
'''
Created on 2017年5月5日

@author: chenyitao
'''

import time


def singleton(cls, *args, **kw):
    '''
    单例模式装饰器
    '''
    instances = {}

    def _singleton():
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]
    return _singleton


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
