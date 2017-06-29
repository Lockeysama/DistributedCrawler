# -*- coding: utf-8 -*-
'''
Created on 2017年4月13日

@author: chenyitao
'''

import time
import os
import hashlib
import json
import re
from base.plugins import DBManager
from conf.default.hbase_site import HBaseSite


class RuleUploader(object):
    '''
    classdocs
    '''
    
    conf_path = ''

    path_base = ''

    hbase_table = ''

    def __init__(self, packages):
        '''
        Constructor
        '''
        self._packages = packages
        if not self._file_check():
            return
        self._storager = DBManager(HBaseSite.random_hbase_node())
        packages_info = self._generator_mould_info()
        print(json.dumps(packages_info, indent=1))
        self._uploader(packages_info)

    def _file_check(self):
        for path in self._packages:
            if not os.path.exists(self.path_base + path):
                print('File Not found: ' + self.path_base + path)
                break
        else:
            return True
        return False

    def _generator_mould_info(self):
        packages_info = {'platform': None, 'packages': []}
        for path in self._packages:
            model_info = {'moulds': []}
            packages_info['platform'], filename = path.split('/')
            model_info['package'] = filename.split('.')[0]
            with open(self.path_base + path, 'r') as f:
                content = f.read().replace(' ', '')
                ret = re.search(r'class(.*?)(ParseRuleBase)', content)
                model_info['moulds'].append(ret.group().replace(" ", '')[5:].split('(')[0] 
                                            if ret else None)
                ret = re.search(r"version='(.*?)'", content)
                model_info['version'] = (ret.group().replace("'", '').split("=")[1] 
                                         if ret else None)
                _md5 = hashlib.md5()
                _md5.update(content)
                model_info['md5'] = _md5.hexdigest()
            packages_info['packages'].append(model_info)
        return packages_info

    def _uploader(self, packages_info, method='ADD'):  # REPLACE_ALL
        platform = packages_info['platform']
        items = {'models': {'index': json.dumps(packages_info)}}
        self._storager.put_to_hbase(self.hbase_table,
                                    platform,
                                    items)
        for path, package in zip(self._packages, packages_info['packages']):
            with open(self.path_base + path, 'r') as f:
                content = f.read()
            items = {'models': {package['package']: content}}
            self._storager.put_to_hbase(self.hbase_table,
                                        packages_info['platform'],
                                        items)
        self._save_conf(packages_info)
        print('Done')

    def _save_conf(self, packages_info):
        platform = packages_info['platform']
        with open(self.conf_path + platform + '.json', 'w') as f:
            f.write(json.dumps(packages_info))


class ProxyRuleUploader(RuleUploader):
    
    path_base = ''
    
    hbase_table = 'tddc_pc_rules'


class ParserModulesUploader(RuleUploader):
    
    conf_path = '/Users/chenyitao/git/tuodao/tddc/conf/parse_rule_index/'
    
    path_base = '/Users/chenyitao/git/tuodao/tddc/worker/parser/parser_moulds/'
    
    hbase_table = 'tddc_platform_conf_table'


def main():
    paths = []
#     paths.append('cheok/cheok_homepage.py')
#     paths.append('cheok/cheok_want_buy_list.py')
#     paths.append('cheok/cheok_want_buy_detail.py')
    paths.append('weidai/show_bid_list.py')
    paths.append('weidai/bid_detail.py')
    paths.append('weidai/bid_detail_extra.py')
    ParserModulesUploader(paths)
    while True:
        time.sleep(60)

if __name__ == '__main__':
    main()