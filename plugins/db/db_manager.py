# -*- coding: utf-8 -*-
'''
Created on 2017年4月12日

@author: chenyitao
'''

import json
import happybase

from log import TDDCLogging


class DBManager(object):
    '''
    classdocs
    '''

    def __init__(self, host_port=None):
        '''
        Constructor
        params:
            host_port:
                EXP: 'localhost:8888'
                DES: HBase的IP、PORT
        '''
        TDDCLogging.info('---->DB Manager Is Starting.')
        self._tables = []
        host, port = host_port.split(':')
        self._hb_pool = happybase.ConnectionPool(size=8,
                                                 host=host,
                                                 port=int(port),
                                                 transport='framed',
                                                 protocol='compact')
        TDDCLogging.info('----->HBase(%s:%s) Was Ready.' % (host, port))
        TDDCLogging.info('---->DB Manager Was Ready.')

    def create_table_to_hbase(self, table, families):
        try:
            with self._hb_pool.connection() as connection:
                connection.create_table(table, families)
        except Exception, e:
            TDDCLogging.error(e)
            return False
        else:
            return True
    
    def _auto_create_table(self, connection, table):
        for cnt in range(2):
            if table not in self._tables:
                if cnt == 1:
                    connection.create_table(table, {k:{} for k in ['source', 'valuable', 'task']})
                    TDDCLogging.warning('Create New Table(%s) to HBase.' % table)
                self._tables = connection.tables()
            else:
                break
    
    def puts_to_hbase(self, table_rows):
        '''
        批量存储
        params:
            table_rows:
                EXP: {'platformxxx': {'row_key1': {'familyxxx': {'column': data},
                                                  {'familyooo': {'column': data}},
                                     {'row_key2': {'familyxxx': {'column': data},
                                                  {'familyooo': {'column': data}}}}
        '''
        try:
            with self._hb_pool.connection() as connection:
                for table, rows in table_rows.items():
                    self._auto_create_table(connection, table)
                    table = connection.table(table)
                    b = table.batch()
                    self._puts(b, rows)
                    b.send()
                return True
        except Exception, e:
            TDDCLogging.error(e)
            return False
    
    def _puts(self, batch, rows):
        for row_key, items in rows.items():
            for family, data in items.items():
                cf_fmt = family + ':'
                values = {}
                for column, value in data.items():
                    if isinstance(value, dict) or isinstance(value, list):
                        value = json.dumps(value)
                    values[cf_fmt + column] = value
                batch.put(row_key, values)
 
    def put_to_hbase(self, table, row_key, items):
        '''
        单个存储
        params:
            items:
                EXP: {'familyxxx': {'column': data},
                      'familyooo': {'column': data}}
        '''
        try:
            with self._hb_pool.connection() as connection:
                self._auto_create_table(connection, table)
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