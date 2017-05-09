# -*- coding: utf-8 -*-
'''
Created on 2017年4月7日

@author: chenyitao
'''

import copy
import json

from common.short_uuid import ShortUUID


class Task(object):

    class Status(object):
        CRAWL_TOPIC = 0
        WAIT_CRAWL = 1
        CRAWL_SUCCESS = 200
        CRAWL_FAILED = 400
        WAIT_PARSE = 1001
        PARSE_SUCCESS = 1200
        PARSE_FAILED = 1400
        WAIT_EXCEPT_PROC = 2001
        EXCEPT_PROC_SUCCESS = 2200
        EXCEPT_PROC_FAILED = 2400

    default_values = {'id': None,
                      'platform': None,
                      'row_key': None,
                      'method': None,
                      'url': None,
                      'feature': None,
                      'status': None,
                      'retry': None,
                      'proxy_type': None,
                      'headers': None}

    def __init__(self, **task_attr):
        self.__dict__ = copy.copy(self.default_values)
        for key in self.__dict__:
            if key in task_attr:
                self.__dict__[key] = task_attr.pop(key)
        if not self.__dict__['id']:
            self.__dict__['id'] = ShortUUID.UUID()
            
    def to_json(self):
        info = {k:v for k,v in self.__dict__.items() if v != None}
        return json.dumps(info)


def main():
    task = Task()
    print(task.__dict__)
    attr = {'id': 'k5pwQctzgzAgKMRcQyFCCC',
            'status': Task.Status.CRAWL_SUCCESS,
            'headers': {'User-Agent': 'Spider'}}
    task2 = Task(**attr)
    print(task2.__dict__)
    js_attr = json.dumps(task2.__dict__)
    print(js_attr)
    task3 = Task(**json.loads(js_attr))
    print(task3.__dict__)
    print(Task(**json.loads(json.dumps(task3.__dict__))).__dict__)
    print(Task(**json.loads(json.dumps(task3.__dict__))).to_json())

if __name__ == '__main__':
    main()
