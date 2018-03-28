# -*- coding: utf-8 -*-
'''
Created on 2017年4月12日

@author: chenyitao
'''

import json
import logging
import random
import time

import gevent
import happybase
from thriftpy.transport import TTransportException

log = logging.getLogger(__name__)


class HBaseManager(happybase.ConnectionPool):

    def __init__(self, nodes):
        self.status = type('HBaseStatus', (), {'alive_timestamp': 0})
        self._nodes = nodes
        self._current_node = random.choice(self._nodes)
        super(HBaseManager, self).__init__(8,
                                           transport='framed',
                                           protocol='compact',
                                           host=str(self._current_node.host),
                                           port=int(self._current_node.port))
        self._tables = []
        gevent.spawn(self._alive_check)
        gevent.sleep()

    def _alive_check(self):
        while True:
            try:
                with self.connection() as _:
                    pass
            except Exception as e:
                self.exception(e)
                log.error('HBase Connection Exception.')
            else:
                self.status.alive_timestamp = int(time.time())
            gevent.sleep(5)

    def get_connection_status(self):
        return self.status

    def get(self, table, row_key, family=None, qualifier=None):
        try:
            with self.connection() as connection:
                table_obj = connection.table(table)
                if family and qualifier:
                    cf = family + ':' + qualifier
                elif family and not qualifier:
                    cf = family
                else:
                    return False, None
                data = table_obj.row(row_key, columns=[cf])
                return bool(len(data)), data
        except TTransportException as e:
            self.exception(e)
            gevent.sleep(1)
            log.debug('Try Again.')
            return self.get(table, row_key, family, qualifier)
        except Exception as e:
            log.exception(e)
            return False, None

    def get_async(self, callback, table, row_key, family=None, qualifier=None, *args, **kwargs):
        def _get(_callback, _table, _row_key, _family=None, _qualifier=None):
            ret = self.get(_table, _row_key, _family, _qualifier)
            _callback(ret, *args, **kwargs)
        gevent.spawn(_get, callback, table, row_key, family, qualifier)
        gevent.sleep()

    def create(self, table, families):
        try:
            with self.connection() as connection:
                connection.create_table(table, families)
        except TTransportException as e:
            log.exception(e)
            gevent.sleep(1)
            log.debug('Try Again.')
            self.create(table, families)
        except Exception as e:
            log.exception(e)
            return False
        else:
            return True

    def _auto_create(self, connection, table, items=None):
        keys = items.keys() if items else ['source', 'valuable', 'task']
        for cnt in range(2):
            if table not in self._tables:
                if cnt == 1:
                    connection.create_table(table, {k: {} for k in keys})
                    log.warning('Create New Table(%s) to HBase.' % table)
                self._tables = connection.tables()
            else:
                break

    def puts(self, table_rows):
        '''
        批量存储
        params:
            table_rows:
                EXP: {'table': {'row_key1': {'family': {'column': data},
                                            {'family': {'column': data}},
                               {'row_key2': {'family': {'column': data},
                                            {'family': {'column': data}}}}
        '''
        try:
            with self.connection() as connection:
                for table, rows in table_rows.items():
                    self._auto_create(connection, table)
                    table_obj = connection.table(table)
                    b = table_obj.batch()
                    self._puts(b, rows)
                    b.send()
                return True
        except TTransportException as e:
            log.exception(e)
            gevent.sleep(1)
            log.debug('Try Again.')
            return self.puts(table_rows)
        except Exception as e:
            log.exception(e)
            return False

    def _puts(self, batch, rows):
        for row_key, items in rows.items():
            for family, data in items.items():
                cf_fmt = family + ':'
                values = {}
                for column, value in data.items():
                    if isinstance(value, dict) or isinstance(value, list):
                        value = json.dumps(value)
                    values[cf_fmt + column] = (value if not isinstance(value, int) and
                                                        not isinstance(value, float) else unicode(value))
                batch.put(row_key, values)

    def put(self, table, row_key, items):
        '''
        单个存储
        params:
            items:
                EXP: {'familyxxx': {'column': data},
                      'familyooo': {'column': data}}
        '''
        try:
            with self.connection() as connection:
                self._auto_create(connection, table, items)
                table_obj = connection.table(table)
                bool_trans_to_number_dict = {True: 1, False: 0}
                for family, data in items.items():
                    cf_fmt = family + ':'
                    values = {}
                    for column, value in data.items():
                        if isinstance(value, dict) or isinstance(value, list):
                            if isinstance(value, bool):
                                value = bool_trans_to_number_dict.get(value)
                            value = json.dumps(value)
                        values[cf_fmt + column] = value
                    table_obj.put(row_key, values)
                return True
        except TTransportException as e:
            log.exception(e)
            gevent.sleep(1)
            log.debug('Try Again.')
            return self.put(table, row_key, items)
        except Exception as e:
            log.exception(e)
            return False
