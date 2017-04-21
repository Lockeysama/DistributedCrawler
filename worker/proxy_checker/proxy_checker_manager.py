# -*- coding: utf-8 -*-
'''
Created on 2017年4月17日

@author: chenyitao
'''
import gevent
import os
import json
import importlib

from conf.base_site import STATUS
from conf.proxy_checker_site import PROXY_CHECKER_CONCURRENT
from common.queues import HTTP_SOURCE_PROXY_QUEUE, HTTPS_SOURCE_PROXY_QUEUE,\
    USEFUL_PROXY_QUEUE, RULES_MOULDS_UPDATE_QUEUE

class CheckerManager(object):
    '''
    classdocs
    '''

    def __init__(self, callback=None):
        '''
        Constructor
        '''
        self._callback = callback
        self._init_rules()
        gevent.spawn(self._rules_update)
        gevent.sleep()
        for i in range(PROXY_CHECKER_CONCURRENT):
            gevent.spawn(self._checker, i, 'http', HTTP_SOURCE_PROXY_QUEUE)
            gevent.sleep()
        for i in range(PROXY_CHECKER_CONCURRENT):
            gevent.spawn(self._checker, i, 'https', HTTPS_SOURCE_PROXY_QUEUE)
            gevent.sleep()
        self._ready()
        
    def _ready(self):
        if self._callback:
            self._callback()
    
    def _init_rules(self):
        base_path = './conf/proxy_checker_rule_index/'
        self._rules_moulds = {'http': {}, 'https': {}}
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
                    platform = index.split('.')[0]
                    self._rules_moulds[cls.proxy_type][platform] = cls
    
    def _rules_update(self):
        while STATUS:
            rule = RULES_MOULDS_UPDATE_QUEUE.get()
            print(rule.platform, rule.package, rule.moulds)
            for cls_name in rule.moulds:
                molule = importlib.import_module(rule.package)
                cls = getattr(molule, cls_name)
                if not cls:
                    print('Exception: import rule failed: '+cls_name)
                    continue
                self._rules_moulds[cls.proxy_type][cls.proxy_type] = cls
    
    def _checker(self, tag, proxy_type, src_queue):
        while STATUS:
            if not len(self._rules_moulds[proxy_type]):
                gevent.sleep(10)
                continue
            info = src_queue.get()
            for platform, cls in self._rules_moulds[proxy_type].items():
                ret = cls(info)
                if ret.useful:
                    info.platform = platform
                    USEFUL_PROXY_QUEUE.put(info)


def main():
    CheckerManager()
    while STATUS:
        gevent.sleep(60)
    
if __name__ == '__main__':
    main()
