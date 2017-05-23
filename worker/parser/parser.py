# -*- coding: utf-8 -*-
'''
Created on 2017年4月11日

@author: chenyitao
'''

import os
import json
import gevent
import importlib

from common.queues import ParserQueues
from common import TDDCLogging


class Parser(object):
    '''
    classdocs
    '''

    def __init__(self, concurrent=8):
        '''
        Constructor
        '''
        TDDCLogging.info('-->Parser Is Starting.')
        self._init_rules()
        self._no_match_rules_task_queue = gevent.queue.Queue()
        gevent.spawn(self._rules_update)
        gevent.sleep()
        gevent.spawn(self._parse)
        gevent.sleep()
        TDDCLogging.info('-->Parser Was Ready.')
    
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
                self._load_moulds(k, v)
    
    def _load_moulds(self, platform, moulds_info):
        rules_path_base = 'worker.parser.parser_moulds.rules'
        for mould_info in moulds_info:
            package = mould_info.get('package', None)
            moulds = mould_info.get('moulds', None)
            if not package or not moulds or not isinstance(moulds, list):
                continue
            module = importlib.import_module('{base}.{platform}.{package}'.format(base=rules_path_base,
                                                                                  platform=platform,
                                                                                  package=package))
            if not module:
                continue 
            for mould in moulds:
                cls = getattr(module, mould)
                if not cls:
                    continue
                feature = cls.__dict__.get('feature', None)
                if not feature:
                    continue
                if not self._rules_moulds.get(platform, None):
                    self._rules_moulds[platform] = {}
                self._rules_moulds[platform][feature] = cls
    
    def _rules_update(self):
        while True:
            rule = ParserQueues.RULES_MOULDS_UPDATE.get()
            TDDCLogging.info(rule.platform + rule.package + rule.moulds)
            for cls_name in rule.moulds:
                molule = importlib.import_module(rule.package)
                cls = getattr(molule, cls_name)
                feature = cls.__dict__.get('feature', None)
                if not feature:
                    TDDCLogging.warning('Exception: import rule failed: ' + cls_name)
                    continue
                platform = rule.platform
                if not self._rules_moulds.get(platform, None):
                    self._rules_moulds[rule.platform] = {}
                self._rules_moulds[rule.platform][feature] = cls
            while not self._no_match_rules_task_queue.empty():
                ParserQueues.WAITING_PARSE.put(self._no_match_rules_task_queue.get())
    
    def _parse(self):
        while True:
            task, body = ParserQueues.WAITING_PARSE.get()
            platform = self._rules_moulds.get(task.platform, None)
            no_match = True
            if platform:
                cls = platform.get(task.feature, None)
                if cls:
                    ret = cls(task, body)
                    self._storage(task, ret.items)
                    self._new_task_push(ret.tasks)
                    fmt = 'Parse: [{platform}:{row_key}:{feature}][S:{items}][N:{tasks}]'
                    TDDCLogging.info(fmt.format(platform=task.platform,
                                                feature=task.feature,
                                                row_key=task.row_key,
                                                items=len(ret.items),
                                                tasks=len(ret.tasks)))
                    no_match = False
            if no_match:
                self._no_match_rules_task_queue.put(task)
                fmt = 'Parse No Match: [P:{platform}][F:{feature}][K:{row_key}]'
                TDDCLogging.warning(fmt.format(platform=task.platform,
                                               feature=task.feature,
                                               row_key=task.row_key))
            else:
                ParserQueues.TASK_STATUS.put(task)

    def _storage(self, task, items):
        if len(items):
            ParserQueues.STORAGE.put([task, items])
    
    def _new_task_push(self, tasks):
        for task in tasks:
            ParserQueues.CRAWL.put(task)
    
    
def main():
    from common.models import Task
    Parser()
    cnt = 100
    gevent.sleep(3)
    while True:
        if cnt > 0:
            parser_task = Task(parse_info_dict={'id': '%d' % cnt, 'status': 3, 'body': 'hello'})
            ParserQueues.WAITING_PARSE.put(parser_task)
            cnt -= 1
            if cnt == 0:
                print('Done')
        gevent.sleep(0.01)
    

if __name__ == '__main__':
    main()