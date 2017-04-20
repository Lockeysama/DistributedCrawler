# -*- coding: utf-8 -*-
'''
Created on 2017年4月12日

@author: chenyitao
'''

import gevent

from conf.proxy_checker_site import PROXY_CHECKER_RULES_HBASE_TABLE, PROXY_CHECKER_RULES_HBASE_FAMILY,\
    PROXY_CHECKER_RULES_HBASE_INDEX_QUALIFIER, PROXY_CHECKER_RULES_CONF_PATH
from base.rule.rules_updater_base import RulesUpdater


class ProxyCheckerRulesUpdater(RulesUpdater):
    '''
    classdocs
    '''

    local_conf_path_base = PROXY_CHECKER_RULES_CONF_PATH
    
    hbase_table = PROXY_CHECKER_RULES_HBASE_TABLE
    
    hbase_family = PROXY_CHECKER_RULES_HBASE_FAMILY
    
    hbase_index_qualifier = PROXY_CHECKER_RULES_HBASE_INDEX_QUALIFIER



def main():
    ProxyCheckerRulesUpdater()
    while True:
        gevent.sleep()

if __name__ == '__main__':
    main()