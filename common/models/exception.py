# -*- coding: utf-8 -*-
'''
Created on 2017年5月5日

@author: chenyitao
'''

import copy
import json
from enum import Enum


TDDCExceptionType = Enum('TDDCExceptionType', ('CrawlerTask404', 'Other'))

class TDDCException(object):
    '''
    classdocs
    '''

    default_values = {'name': None,
                      'desc': None,
                      'e_type': None,
                      'detail': None}

    def __init__(self, **task_attr):
        self.__dict__ = copy.copy(self.default_values)
        for key in self.__dict__:
            if key in task_attr:
                self.__dict__[key] = task_attr.pop(key)
            
    def to_json(self):
        info = {k:v for k,v in self.__dict__.items() if v != None}
        return json.dumps(info)


def main():
    e = TDDCException(name='Crawl Task 404',
                      e_type=TDDCExceptionType.CrawlerTask404,
                      detail='{"url": "http://a.com"}')
    print(e)

if __name__ == '__main__':
    main()
