# -*- coding: utf-8 -*-
'''
Created on 2017年4月13日

@author: chenyitao
'''

import time
import os
import hashlib
from plugins.db.db_manager import DBManager
import json
import importlib
from conf.parser_site import PARSE_RULES_HBASE_TABLE, PARSE_RULES_HBASE_FAMILY, PARSE_RULES_HBASE_INDEX_QUALIFIER

class RuleUploader(object):
    '''
    classdocs
    '''
    
    hbase_table = ''

    def __init__(self, rule_path, platform, module_name, package):
        '''
        Constructor
        '''
        self._rule_path = rule_path
        if not self._file_check():
            return
        self._platform = platform
        self._module_name = module_name
        self._package = package
        self._wait = True
        def _db_ready(params=None):
            self._wait = False
        self._db = DBManager('Rule Updater', _db_ready) 
        while self._wait:
            time.sleep(0.2)
        print('Rule Uploader Tool Was Ready.')

    def _file_check(self):
        if not os.path.exists(self._rule_path):
            print('File Not found: ' + self._rule_path)
            return False
        return True
    
    def upload(self):
        file_content = None
        try:
            with open(self._rule_path, 'r') as f:
                file_content = f.read()
        except Exception, e:
            print(e)
        else:
            if not file_content:
                print('File Load Exception.')
                return
            _md5 = hashlib.md5()
            _md5.update(file_content)
            file_md5 = _md5.hexdigest()
            item = {'index': [{'package': self._package,
                               'moulds': self._module_name,
                               'md5': file_md5}],
                    self._package.split('.')[-1]: file_content}
            self._db.hbase_instance().put(self.hbase_table, self._platform, item=item, family='rules')


class ProxyRuleUploader(RuleUploader):
    
    hbase_table = 'tddc_pc_rules'
        

def main():
    path = '../worker/proxy_checker/moulds/cheok.py'
    proxy_rule_uploader = ProxyRuleUploader(path,
                                            'cheok',
                                            ['CheokProxyChecker'],
                                            'worker.proxy_checker.moulds.cheok')
    proxy_rule_uploader.upload()
    while True:
        time.sleep(60)

if __name__ == '__main__':
    main()