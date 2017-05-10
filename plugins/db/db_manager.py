# -*- coding: utf-8 -*-
'''
Created on 2017年4月12日

@author: chenyitao
'''

from .hbase_manager.hbase_manager import HBaseManager
from common import TDDCLogging


class DBManager(object):
    '''
    classdocs
    '''

    def __init__(self, tag, host_ports=None, callback=None):
        '''
        Constructor
        '''
        self._tag = tag
        TDDCLogging.info('---->DB Manager(%s) Is Starting.' % self._tag)
        self._hbase_status = False
        self._callback =callback
        self._hbase_manager = HBaseManager(host_ports, self._db_manager_was_ready)
        
    def _db_manager_was_ready(self):
        TDDCLogging.info('---->DB Manager(%s) Was Ready.' % self._tag)
        self._hbase_status = True
        if self._callback:
            self._callback()
    
    def hbase_instance(self):
        if self._hbase_status:
            return self._hbase_manager
        else:
            TDDCLogging.warning('HBase Is Not Ready.')
            return None
        
    def put_to_hbase(self, table, row_key, items):
        if self.hbase_instance():
            try:
                return self.hbase_instance().put(table, row_key, items)
            except Exception, e:
                TDDCLogging.warning('put_to_hbase', e)
            return False


def main():
    pass

if __name__ == '__main__':
    main()