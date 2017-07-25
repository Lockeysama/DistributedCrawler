# -*- coding: utf-8 -*-
'''
Created on 2017年4月7日

@author: chenyitao
'''

import copy
import time
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

    default_values = {'id': None,  # 任务ID；ShortUUID生成
                      'task_type': None,  # 任务类型；None默认类型，1: 增量爬虫类型(包括cookie变化、参数变化但URL不变的类型)
                      'platform': None,  # 任务平台标识；存储时为表名（测试环境加后缀 '_test'）
                      'row_key': None,  # 存储Key（URL的MD5）
                      'method': None,  # 请求方法；默认None则当成GET处理
                      'url': None,  # 任务URL
                      'feature': None,  # 任务特征；用于解析网页时自动识别解析模块
                      'status': None,  # 任务状态
                      'retry': None,  # 任务重试次数；默认3次
                      'proxy_type': None,  # 代理类型：是否加代理
                      'cookie': None,  # Cookie
                      'headers': None,  # HTTP请求头部；dict类型
                      'timestamp': None}  # 任务时间戳

    def __init__(self, **task_attr):
        self.__dict__ = copy.copy(self.default_values)
        for key in self.__dict__:
            if key in task_attr:
                self.__dict__[key] = task_attr.pop(key)
        if not self.__dict__['id']:
            self.__dict__['id'] = ShortUUID.UUID()
        if task_attr.get('reflush_time', False) or not self.__dict__['timestamp']:
            self.timestamp = time.time()

    def to_json(self):
        info = {k:v for k,v in self.__dict__.items() if v != None}
        return json.dumps(info)
    
    def __repr__(self, *args, **kwargs):
        return self.to_json()


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
