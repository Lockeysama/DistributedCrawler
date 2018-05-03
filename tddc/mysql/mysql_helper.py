# encoding: utf-8
"""
@version: ??
@author: chenyitao
@license: Apache Licence 
@software: PyCharm
@file: mysql_helper.py
@time: 2018/4/9 19:57
"""
import logging

import MySQLdb

from ..worker.models import MySQLModel, DBSession
from ..util.util import Singleton


log = logging.getLogger(__name__)


class MySQLHelper(object):
    __metaclass__ = Singleton

    def __init__(self):
        self.conf = DBSession.query(MySQLModel).get(1)
        self.db = MySQLdb.Connect(host=self.conf.host,
                                  port=self.conf.port,
                                  user=self.conf.username,
                                  passwd=self.conf.passwd,
                                  db=self.conf.db,
                                  charset='utf8',
                                  autocommit=True)

    def replace(self, table, **fields_values):
        cursor = self.db.cursor()
        fields = ','.join(fields_values.keys())
        values = [v.encode('utf-8') if isinstance(v, unicode) else v for v in fields_values.values()]
        values = ','.join(['\'{}\''.format(v) if isinstance(v, str) else '{}'.format(v) for v in values])
        sql = 'REPLACE INTO {} ({}) VALUES ({});'.format(table, fields, values)
        try:
            cursor.execute(sql)
        except Exception as e:
            log.warning(e)
        finally:
            cursor.close()
        self.db.commit()

    # def replace_mutil(self, table, fields, *fields_values):
    #     if not len(fields_values):
    #         return
    #     fields.sort()
    #     fields_str = ','.join(fields)
    #     values = []
    #     for fv in fields_values:
    #         ks = fv.keys()
    #         ks.sort()
    #         fv_values = [fv[k].encode('utf-8')
    #                      if isinstance(fv.get(k), unicode)
    #                      else (fv.get(k) if fv.get(k) is not None else 'null')
    #                      for k in fields]
    #         v = ', '.join(['\'{}\''.format(v.encode('utf-8'))
    #                        if isinstance(v, str) and v != 'null'
    #                        else str(v)
    #                        for v in fv_values])
    #         values.append('({})'.format(v))
    #     cursor = self.db.cursor()
    #     vs_str = ', '.join(values)
    #     sql = 'REPLACE INTO {} ({}) VALUES {};'.format(table, fields_str, vs_str)
    #     try:
    #         cursor.execute(sql)
    #     except Exception as e:
    #         log.warning(e)
    #     finally:
    #         cursor.close()

    def replace_mutil(self, table, fields, *fields_values):
        if not len(fields_values):
            return
        fields.sort()
        fields_str = ','.join(fields)
        values = []
        for fv in fields_values:
            ks = fv.keys()
            ks.sort()
            fv_values = [fv[k].encode('utf-8')
                         if isinstance(fv.get(k), unicode)
                         else (fv.get(k) if fv.get(k) is not None else 0)
                         for k in fields]
            v = ', '.join(['\'{}\''.format(v.encode('utf-8'))
                           if isinstance(v, str) and v != 'null'
                           else str(v)
                           for v in fv_values])
            values.append('({})'.format(v))
        _values = []
        if len(values) > 100:
            pre_index = 0
            for index in range(100, len(values), 100):
                _values.append(values[pre_index:index])
                pre_index = index
            if pre_index + 100 > len(values):
                _values.append(values[-(len(values) - pre_index):])
        else:
            _values.append(values)
        cursor = self.db.cursor()
        try:
            for vs in _values:
                vs_str = ', '.join(vs)
                sql = 'REPLACE INTO {} ({}) VALUES {};'.format(table, fields_str, vs_str)
                cursor.execute(sql)
        except Exception as e:
            log.warning(e)
        finally:
            cursor.close()
            self.db.commit()

    def update(self, table, query, **update_values):
        cursor = self.db.cursor()
        update_values = {k: v.encode('utf-8') if isinstance(v, unicode) else v for k, v in update_values.items()}
        new_values = ','.join(['{}='.format(k) + ('\'{}\''.format(v) if isinstance(v, str) else '{}'.format(v))
                              for k, v in update_values.items()])
        query = {k: v.encode('utf-8') if isinstance(v, unicode) else v for k, v in query.items()}
        query_str = ' AND '.join(['{}='.format(k) + ('\'{}\''.format(v)
                                                     if isinstance(v, str)
                                                     else '{}'.format(v))
                                  for k, v in query.items()])
        if query:
            query_str = ' WHERE ' + query_str
        else:
            query_str = ''
        sql = 'UPDATE {} SET {}{};'.format(table, new_values, query_str)
        try:
            cursor.execute(sql)
        except Exception as e:
            log.warning(e)
        finally:
            cursor.close()

    def select(self, table, *fields, **query):
        cursor = self.db.cursor()
        query = {k: v.encode('utf-8') if isinstance(v, unicode) else v for k, v in query.items()}
        fields = ','.join(fields)
        query_str = ' AND '.join(['{}='.format(k) + ('\'{}\''.format(v)
                                                     if isinstance(v, str)
                                                     else '{}'.format(v))
                                  for k, v in query.items()])
        if query:
            query_str = ' WHERE ' + query_str
        else:
            query_str = ''
        sql = 'SELECT {} FROM {}{};'.format(fields, table, query_str)
        try:
            ret = cursor.execute(sql)
            if ret:
                ret = cursor.fetchall()
        except Exception as e:
            ret = 0
            log.warning(e)
        finally:
            cursor.close()
        return ret
