# -*- coding: utf-8 -*-
'''
Created on 2017年4月11日

@author: chenyitao
'''

import os
import json
import Queue
import gevent
import importlib

from common.queues import WAITING_PARSE_QUEUE, STORAGE_QUEUE, \
    PARSER_RULES_MOULDS_UPDATE_QUEUE,CRAWL_QUEUE
from conf.base_site import STATUS

SIGNAL_PARSER_READY = object()

class ParserManager(object):
    '''
    classdocs
    '''

    def __init__(self, callback=None, concurrent=8):
        '''
        Constructor
        '''
        print('-->Parser Is Starting.')
        self._callback = callback
        self._init_rules()
        self._no_match_rules_task_queue = Queue.Queue()
        gevent.spawn(self._rules_update)
        gevent.sleep()
        for i in range(concurrent):
            gevent.spawn(self._parse, i)
            gevent.sleep()
        self._ready()
    
    def _init_rules(self):
        base_path = './conf/parse_rule_index/'
        self._rules_moulds = {}
        indexs = os.listdir(base_path)
        for index in indexs:
            path = base_path + index
            with open(path, 'r') as f:
                conf = json.loads(f.read())
            if not isinstance(conf, dict):
                continue
            for k, v in conf.items():
                module = importlib.import_module(k)
                moulds = v.get('moulds', None)
                if not isinstance(moulds, list):
                    continue
                for mould in moulds:
                    cls = getattr(module, mould)
                    if not cls:
                        continue
                    feature = cls.__dict__.get('feature', None)
                    if not feature:
                        continue
                    platform = index.split('.')[0]
                    if not self._rules_moulds.get(platform, None):
                        self._rules_moulds[platform] = {}
                    self._rules_moulds[platform][feature] = cls
    
    def _rules_update(self):
        while STATUS:
            rule = PARSER_RULES_MOULDS_UPDATE_QUEUE.get()
            print(rule.platform, rule.package, rule.moulds)
            for cls_name in rule.moulds:
                molule = importlib.import_module(rule.package)
                cls = getattr(molule, cls_name)
                feature = cls.__dict__.get('feature', None)
                if not feature:
                    print('Exception: import rule failed: '+cls_name)
                    continue
                platform = rule.platform
                if not self._rules_moulds.get(platform, None):
                    self._rules_moulds[rule.platform] = {}
                self._rules_moulds[rule.platform][feature] = cls
            while not self._no_match_rules_task_queue.empty():
                WAITING_PARSE_QUEUE.put(self._no_match_rules_task_queue.get())
    
    def _parse(self, tag):
        while STATUS:
            task = WAITING_PARSE_QUEUE.get()
            platform = self._rules_moulds.get(task.platform, None)
            no_match = True
            if platform:
                cls = platform.get(task.feature, None)
                if cls:
                    ret = cls(task)
                    if len(ret.items):
                        self._storage(task, ret.items)
                    self._new_task_push(ret.tasks)
                    fmt = 'Parse: [P:{platform}][F:{feature}][K:{row_key}][S:{items}][N:{tasks}]'
                    print(fmt.format(platform=task.platform,
                                     feature=task.feature,
                                     row_key=task.row_key,
                                     items=len(ret.items),
                                     tasks=len(ret.tasks)))
                    no_match = False
            if no_match:
                self._no_match_rules_task_queue.put(task)
                print('Parse No Match: [P:{platform}][F:{feature}][K:{row_key}]'.format(platform=task.platform,
                                                                                        feature=task.feature,
                                                                                        row_key=task.row_key))

    def _storage(self, task, items):
        STORAGE_QUEUE.put([task, items])
    
    def _new_task_push(self, tasks):
        for task in tasks:
            CRAWL_QUEUE.put(task)
    
    def _ready(self):
        print('-->Parser Was Ready.')
        if self._callback:
            self._callback(self, SIGNAL_PARSER_READY, self)
        
        
def main():
    from worker.parser.models.parse_task import ParseTask
    ParserManager()
    cnt = 100
    gevent.sleep(3)
    while True:
        if cnt > 0:
            parser_task = ParseTask(parse_info_dict={'id': '%d' % cnt, 'status': 3, 'body': 'hello'})
            WAITING_PARSE_QUEUE.put(parser_task)
            cnt -= 1
            if cnt == 0:
                print('Done')
        gevent.sleep(0.01)
    

if __name__ == '__main__':
    main()