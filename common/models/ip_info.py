# -*- coding: utf-8 -*-
'''
Created on 2017年5月23日

@author: chenyitao
'''

import copy
import json


class IPInfo(object):
    '''
    classdocs
    '''

    default_values = {'ip_port': None,  # IP:PORT
                      'http_or_https': None,  # 代理类型；None默认类型，1: HTTP
                      'platform': None}  # 任务平台标识

    def __init__(self, **attr):
        self.__dict__ = copy.copy(self.default_values)
        for key in self.__dict__:
            if key in attr:
                self.__dict__[key] = attr.pop(key)
            
    def to_json(self):
        info = {k:v for k,v in self.__dict__.items() if v != None}
        return json.dumps(info)
