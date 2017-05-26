# -*- coding: utf-8 -*-
'''
Created on 2017年4月17日

@author: chenyitao
'''
import gevent
import os
import json
import importlib

from conf import ProxyCheckerSite
from common.queues import ProxyCheckerQueues
from log import TDDCLogging


class Checker(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        TDDCLogging.info('-->Checker Is Starting.')
        self._init_rules()
        gevent.spawn(self._rules_update)
        gevent.sleep()
        for i in range(ProxyCheckerSite.CONCURRENT):
            gevent.spawn(self._check, i, 'http', ProxyCheckerQueues.HTTP_SOURCE_PROXY)
            gevent.sleep()
        for i in range(ProxyCheckerSite.CONCURRENT):
            gevent.spawn(self._check, i, 'https', ProxyCheckerQueues.HTTPS_SOURCE_PROXY)
            gevent.sleep()
        TDDCLogging.info('-->Checker Was Started.')

    def _init_rules(self):
        base_path = ProxyCheckerSite.RULES_CONF_PATH_BASE
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
        while True:
            rule = ProxyCheckerQueues.RULES_MOULDS_UPDATE.get()
            print(rule.platform, rule.package, rule.moulds)
            for cls_name in rule.moulds:
                molule = importlib.import_module(rule.package)
                cls = getattr(molule, cls_name)
                if not cls:
                    TDDCLogging.error('Exception: import rule failed: '+cls_name)
                    continue
                self._rules_moulds[cls.proxy_type][cls.proxy_type] = cls
    
    def _check(self, tag, proxy_type, src_queue):
        while True:
            if not len(self._rules_moulds[proxy_type]):
                gevent.sleep(10)
                continue
            info = src_queue.get()
            for platform, cls in self._rules_moulds[proxy_type].items():
                ret = cls(info)
                if ret.useful:
                    info.platform = platform
                    ProxyCheckerQueues.USEFUL_PROXY.put(info)


def main():
    Checker()
    while True:
        gevent.sleep(60)
    
if __name__ == '__main__':
    main()
