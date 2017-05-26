# -*- coding: utf-8 -*-
'''
Created on 2017年5月8日

@author: chenyitao
'''

import gevent

from log import TDDCLogging
from conf.default import HBaseSite

from plugins import DBManager


class StoragerBase(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        TDDCLogging.info('-->Storager Manager Is Starting.')
        self._db = DBManager(HBaseSite.random_hbase_node())
        gevent.spawn(self._push)
        gevent.sleep()
        gevent.spawn(self._pull)
        gevent.sleep()
        TDDCLogging.info('-->Storager Manager Was Ready.')

    def push_onec(self, table, row_key, family, qualifier, content):
        storage_items = {'models': {family: {qualifier: content}}}
        if not self._db.put_to_hbase(table, 
                                     row_key,
                                     storage_items):
            return False
        return True

    def _push(self):
        pass
    
    def pull_once(self, table, row_key, family=None, qualifier=None):
        success, ret = self._db.get_from_hbase(table,
                                               row_key,
                                               family,
                                               qualifier)
        if not success or not ret:
            return success, ret
        values = []
        for _, value in ret.items():
            values.append(value)
        return True, values
    
    def _pull(self):
        pass


def main():
    pass

if __name__ == '__main__':
    main()
