# -*- coding: utf-8 -*-
'''
Created on 2017年4月12日

@author: chenyitao
'''

import gevent

from conf import ProxyCheckerSite
from base import RulesUpdater


class ProxyCheckerRulesUpdater(RulesUpdater):
    '''
    classdocs
    '''

    local_conf_path_base = ProxyCheckerSite.RULES_CONF_PATH
    
    hbase_table = ProxyCheckerSite.RULES_TABLE
    
    hbase_family = ProxyCheckerSite.RULES_FAMILY
    
    hbase_index_qualifier = ProxyCheckerSite.RULES_QUALIFIER


def main():
    ProxyCheckerRulesUpdater()
    while True:
        gevent.sleep()

if __name__ == '__main__':
    main()