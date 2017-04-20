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

class ParseRulesUpload(object):
    '''
    classdocs
    '''

    def __init__(self, callback=None):
        '''
        Constructor
        '''
        self._callback = callback
        self._wait = True
        def _db_ready(params=None):
            self._wait = False
        self._db = DBManager('Rules Updater', _db_ready) 
        while self._wait:
            time.sleep(0.2)
        print('Parse Rules Upload Tools Was Ready.')
                        
    def download_test(self, platform):
        _update_list = []
        _local_conf = {}
        conf_path = '../conf/parse_rule_index/%s.json' % platform
        if os.path.exists(conf_path):
            with open(conf_path, 'r') as f:
                _local_conf = json.loads(f.read())
        ret = self._db.hbase_instance().get(PARSE_RULES_HBASE_TABLE,
                                            platform,
                                            PARSE_RULES_HBASE_FAMILY,
                                            PARSE_RULES_HBASE_INDEX_QUALIFIER)
        for column_value in ret.columnValues:
            _remote_conf = json.loads(column_value.value)
            _mould_name = _remote_conf['mould_name']
            _remote__md5 = _remote_conf['md5']
            _local_md5 = _local_conf.get(_mould_name, None)
            if _local_md5 == _remote__md5:
                continue
            _update_list.append(_remote_conf)
        for item in _update_list:
            _mould_name = item['mould_name']
            _md5 = item['md5']
            ret = self._db.hbase_instance().get(PARSE_RULES_HBASE_TABLE,
                                                platform,
                                                PARSE_RULES_HBASE_FAMILY,
                                                _mould_name)
            for column_value in ret.columnValues:
                with open(_mould_name.split('.')[-1]+'.py', 'a') as f:
                    f.write(column_value.value)
        m = importlib.import_module(_mould_name.split('.')[-1])
        print(m)
    
    def upload(self, file_path, platform, module_name, package):
        _file_content = None
        try:
            with open(file_path, 'r') as f:
                _file_content = f.read()
        except Exception, e:
            print(e)
        else:
            if not _file_content:
                print('File Load Exception.')
                return
            _md5 = hashlib.md5()
            _md5.update(_file_content)
            file_md5 = _md5.hexdigest()
            item = {PARSE_RULES_HBASE_INDEX_QUALIFIER: [{'package': package,
                                                         'moulds': module_name,
                                                         'md5': file_md5}],
                    package.split('.')[-1]: _file_content}
            self._db.hbase_instance().put(PARSE_RULES_HBASE_TABLE, platform, item=item, family='rules')

        
def main():
    uploder = ParseRulesUpload()
    uploder.upload('../worker/parser/parser_moulds/rules/test/rule_test.py',
                   'task_test',
                   ['RulesTest'],
                   'worker.parser.parser_moulds.rules.cheok.cheok_homepage')
#     uploder.download_test('test2')
    while True:
        time.sleep(60)

if __name__ == '__main__':
    main()