# -*- coding: utf-8 -*-
"""
@author  : chenyitao
@email   : yt.chen@bshier.com
@license: Apache Licence
@software: PyCharm
@file    : pymysql_ex.py
@time    : 2018/8/15 11:06
"""
import gevent
import pymysql
import logging

from tddc import MySQLModel, DBSession, Singleton

log = logging.getLogger(__name__)


class PyMySQLEx(object):

    __metaclass__ = Singleton

    def __init__(self):
        self.conf = DBSession.query(MySQLModel).get()
        self.db = self.connect()

    def connect(self):
        return pymysql.connect(
            host=self.conf.host, port=self.conf.port, user=self.conf.username,
            passwd=self.conf.passwd, db=self.conf.db, charset='utf8',
            autocommit=True, cursorclass=pymysql.cursors.DictCursor)

    def replace(self, table, **fields_values):
        fields = ','.join(fields_values.keys())
        values = [v.encode('utf-8') if isinstance(v, unicode) else v for v in fields_values.values()]
        values = ','.join(['\'{}\''.format(v) if isinstance(v, str) else '{}'.format(v) for v in values])
        sql = 'REPLACE INTO {} ({}) VALUES ({});'.format(table, fields, values)
        with self.db.cursor() as cursor:
            try:
                cursor.execute(sql)
            except pymysql.OperationalError as e:
                log.exception(e)
                self.db = self.connect()
                gevent.sleep(3)
                return self.replace(table, **fields_values)
            except Exception as e:
                log.warning(e)
            self.db.commit()

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
            v = ', '.join(['\'{}\''.format(v)
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
        with self.db.cursor() as cursor:
            try:
                for vs in _values:
                    vs_str = ', '.join(vs)
                    sql = 'REPLACE INTO {} ({}) VALUES {};'.format(table, fields_str, vs_str)
                    cursor.execute(sql)
            except pymysql.OperationalError as e:
                log.exception(e)
                self.db = self.connect()
                gevent.sleep(3)
                return self.replace_mutil(table, fields, *fields_values)
            except Exception as e:
                log.exception(e)

    def update(self, table, query, **update_values):
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
        with self.db.cursor() as cursor:
            try:
                cursor.execute(sql)
            except pymysql.OperationalError as e:
                log.exception(e)
                self.db = self.connect()
                gevent.sleep(3)
                return self.update(table, query, **update_values)
            except Exception as e:
                log.warning(e)

    def select(self, table, *fields, **query):
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
        with self.db.cursor() as cursor:
            try:
                ret = cursor.execute(sql)
                if ret:
                    ret = cursor.fetchall()
            except pymysql.OperationalError as e:
                log.exception(e)
                self.db = self.connect()
                gevent.sleep(3)
                return self.select(table, *fields, **query)
            except Exception as e:
                ret = 0
                log.warning(e)
        return ret

    def select_with(self, table, fields, query=None):
        fields_str = ','.join(fields) if isinstance(fields, list) else fields
        query_str = (' WHERE ' + query) if query else ''
        sql = 'SELECT {} FROM {} {};'.format(fields_str, table, query_str)
        with self.db.cursor() as cursor:
            try:
                ret = cursor.execute(sql)
                if ret:
                    ret = cursor.fetchall()
            except pymysql.OperationalError as e:
                log.exception(e)
                self.db = self.connect()
                gevent.sleep(3)
                return self.select_with(table, fields, query)
            except Exception as e:
                ret = None
                log.warning(e)
        return ret

    def exec_procedure(self, procedure_name, args):
        try:
            with self.db.cursor() as cursor:
                cursor.callproc(procedure_name, args)
        except pymysql.OperationalError as e:
            log.exception(e)
            self.db = self.connect()
            gevent.sleep(3)
            return self.exec_procedure(procedure_name, args)
        except Exception as e:
            log.exception(e)

    def exec_procedures(self, procedure_name, args_list):
        try:
            with self.db.cursor() as cursor:
                for args in args_list:
                    cursor.callproc(procedure_name, args)
        except pymysql.OperationalError as e:
            log.exception(e)
            self.db = self.connect()
            gevent.sleep(3)
            return self.exec_procedures(procedure_name, args_list)
        except Exception as e:
            log.exception(e)

    def __del__(self):
        self.db.close()

    def delete_with(self, table, query_str=None):
        sql = 'DELETE FROM {} {};'.format(
            table, 'WHERE {}'.format(query_str) if query_str else ''
        )
        with self.db.cursor() as cursor:
            try:
                cursor.execute(sql)
            except pymysql.OperationalError as e:
                log.exception(e)
                self.db = self.connect()
                gevent.sleep(3)
                return self.delete_with(table, query_str)
            except Exception as e:
                log.warning(e)
