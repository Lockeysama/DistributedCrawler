# -*- coding: utf-8 -*-
'''
Created on 2017年4月12日

@author: chenyitao
'''

import json
import happybase

from common import TDDCLogging


class DBManager(object):
    '''
    classdocs
    '''

    def __init__(self, tag, host_port=None):
        '''
        Constructor
        '''
        TDDCLogging.info('---->DB Manager(%s) Is Starting.' % self._tag)
        self._tag = tag
        self._tables = []
        host, port = host_port.split(':')
        self._hb_pool = happybase.ConnectionPool(size=2,
                                                 host=host,
                                                 port=int(port),
                                                 transport='framed',
                                                 protocol='compact')
        TDDCLogging.info('---->DB Manager(%s) Was Ready.' % self._tag)
    
    def create_table_to_hbase(self, table, families):
        try:
            with self._hb_pool.connection() as connection:
                connection.create_table(table, families)
        except Exception, e:
            TDDCLogging.error(e)
            return False
        else:
            return True
    
    def put_to_hbase(self, table, row_key, items):
        try:
            with self._hb_pool.connection() as connection:
                for cnt in range(2):
                    if table not in self._tables:
                        if cnt == 1:
                            connection.create_table(table, items.keys())
                            TDDCLogging.warning('Create New Table(%s) to HBase.' % table)
                        self._tables = connection.tables()
                    else:
                        break
                table = connection.table(table)
                for family, data in items.items():
                    cf_fmt = family + ':'
                    values = {}
                    for column, value in data.items():
                        if isinstance(value, dict) or isinstance(value, list):
                            value = json.dumps(value)
                        values[cf_fmt + column] = value
                    table.put(row_key, values) 
                return True
        except Exception, e:
            TDDCLogging.error(e)
            return False
    
    def get_from_hbase(self, table, row_key, family=None, qualifier=None):
        try:
            with self._hb_pool.connection() as connection:
                table = connection.table(table)
                if family and qualifier:
                    cf = family + ':' + qualifier
                elif family and not qualifier:
                    cf = family
                else:
                    return False, None
                return True, table.row(row_key, columns=[cf])
        except Exception, e:
            TDDCLogging.error(e)
            return False, None


def main():
    pass

if __name__ == '__main__':
    main()