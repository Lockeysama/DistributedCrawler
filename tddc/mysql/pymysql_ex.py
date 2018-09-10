# -*- coding: utf-8 -*-
"""
@author  : chenyitao
@email   : yt.chen@bshier.com
@license: Apache Licence
@software: PyCharm
@file    : pymysql_ex.py
@time    : 2018/8/15 11:06
"""
import MySQLdb
from MySQLdb.cursors import DictCursor
from collections import defaultdict
from gevent.queue import Queue
import logging

from tddc import MySQLModel, DBSession, Singleton

log = logging.getLogger(__name__)


class PyMySQLEx(object):

    __metaclass__ = Singleton

    def __init__(self, conf=None, size=10):
        self.dbs = defaultdict(Queue)
        self.conf = defaultdict(MySQLModel)
        all_conf = DBSession.query(MySQLModel).all() if not conf else [conf]
        for conf in all_conf:
            [self.dbs[conf.name].put(self.connect(conf)) for _ in range(size)]
            self.conf[conf.name] = conf

    @staticmethod
    def connect(conf):
        return MySQLdb.Connect(
            host=conf.host, port=conf.port, user=conf.username,
            passwd=conf.passwd, db=conf.db, charset='utf8', autocommit=True,
            cursorclass=DictCursor
        )

    def exec_sql(self, **kwargs):
        db_instance_name = kwargs.get('db_instance_name')
        sql = kwargs.get('sql')
        if not self.dbs.get(db_instance_name, None):
            log.warning('DB[{}] Not Found.'.format(db_instance_name))
            return None
        db = self.dbs.get(db_instance_name).get()
        records = None
        cursor = None
        try:
            cursor = db.cursor()
            cursor.execute(sql)
            records = cursor.fetchall()
            cursor.close()
        except MySQLdb.OperationalError as e:
            cursor.close()
            log.exception(e)
            self.dbs.get(db_instance_name).put(self.connect(self.conf.get(db_instance_name)))
            gevent.sleep(3)
            return self.exec_sql(**kwargs)
        except Exception as e:
            cursor.close()
            log.warning(e)
        self.dbs.get(db_instance_name).put(db)
        return records

    def insert(self, db_instance_name, table, **fields_values):
        fields = ','.join(fields_values.keys())
        values = [v.encode('utf-8') if isinstance(v, unicode) else v for v in fields_values.values()]
        values = ','.join(['\'{}\''.format(v) if isinstance(v, str) else '{}'.format(v) for v in values])
        sql = 'INSERT INTO {} ({}) VALUES ({});'.format(table, fields, values)
        self.exec_sql(**{'db_instance_name': db_instance_name, 'sql': sql})

    def insert_many(self, db_instance_name, table, fields, *fields_values_list):
        if not len(fields_values_list):
            return
        fields.sort()
        fields_str = ','.join(fields)
        values = []
        for fv in fields_values_list:
            fv_values = [fv[k].encode('utf-8')
                         if isinstance(fv.get(k), unicode)
                         else (fv.get(k) if fv.get(k) is not None else 0)
                         for k in fields]
            v = ', '.join(['\'{}\''.format(v) if isinstance(v, str) and v != 'null' else str(v)
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
        for vs in _values:
            vs_str = ', '.join(vs)
            sql = 'INSERT INTO {} ({}) VALUES {};'.format(table, fields_str, vs_str)
            self.exec_sql(**{'db_instance_name': db_instance_name, 'sql': sql})

    def replace(self, db_instance_name, table, **fields_values):
        fields = ','.join(fields_values.keys())
        values = [v.encode('utf-8') if isinstance(v, unicode) else v for v in fields_values.values()]
        values = ','.join(['\'{}\''.format(v) if isinstance(v, str) else '{}'.format(v) for v in values])
        sql = 'REPLACE INTO {} ({}) VALUES ({});'.format(table, fields, values)
        self.exec_sql(**{'db_instance_name': db_instance_name, 'sql': sql})

    def replace_many(self, db_instance_name, table, fields, *fields_values_list):
        if not len(fields_values_list):
            return
        fields.sort()
        fields_str = ','.join(fields)
        values = []
        for fv in fields_values_list:
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
        for vs in _values:
            vs_str = ', '.join(vs)
            sql = 'REPLACE INTO {} ({}) VALUES {};'.format(table, fields_str, vs_str)
            self.exec_sql(**{'db_instance_name': db_instance_name, 'sql': sql})

    def delete(self, db_instance_name, table, query_str=None):
        sql = 'DELETE FROM {} {};'.format(
            table, 'WHERE {}'.format(query_str) if query_str else ''
        )
        self.exec_sql(**{'db_instance_name': db_instance_name, 'sql': sql})

    def update(self, db_instance_name, table, query, **fields_values):
        update_values = {k: v.encode('utf-8') if isinstance(v, unicode) else v
                         for k, v in fields_values.items()}
        new_values = ','.join(['{}='.format(k) + ('\'{}\''.format(v) if isinstance(v, str) else '{}'.format(v))
                              for k, v in update_values.items()])
        query_str = ' WHERE {} '.format(query) if query else ''
        sql = 'UPDATE {} SET {} {};'.format(table, new_values, query_str)
        self.exec_sql(**{'db_instance_name': db_instance_name, 'sql': sql})

    def update_many(self, db_instance_name, table, *fields_values_list):
        sqls = []
        for fields_values, query in fields_values_list:
            update_values = {k: v.encode('utf-8') if isinstance(v, unicode) else v
                             for k, v in fields_values.items()}
            new_values = ','.join(['{}='.format(k) + ('\'{}\''.format(v) if isinstance(v, str) else '{}'.format(v))
                                  for k, v in update_values.items()])
            query_str = ' WHERE {} '.format(query) if query else ''
            sql = 'UPDATE {} SET {} {};'.format(table, new_values, query_str)
            sqls.append(sql)
            if len(sqls) == 100:
                self.exec_sql(**{'db_instance_name': db_instance_name, 'sql': ''.join(sqls)})
                sqls = []
        if sqls:
            self.exec_sql(**{'db_instance_name': db_instance_name, 'sql': ''.join(sqls)})

    def select(self, db_instance_name, table, fields=None, query=''):
        if not fields:
            fields = '*'
        fields_str = ','.join(fields) if isinstance(fields, list) or isinstance(fields, tuple) else fields
        query_str = ' WHERE {} '.format(query) if query else ''
        sql = 'SELECT {} FROM {} {};'.format(fields_str, table, query_str)
        return self.exec_sql(**{'db_instance_name': db_instance_name, 'sql': sql})

    def exec_procedure(self, db_instance_name, procedure_name, args):
        db = self.dbs.get(db_instance_name).get()
        try:
            with db.cursor() as cursor:
                cursor.callproc(procedure_name, args)
        except pymysql.OperationalError as e:
            log.exception(e)
            self.dbs.get(db_instance_name).put(self.connect(self.conf.get(db_instance_name)))
            gevent.sleep(3)
            return self.exec_procedure(procedure_name, args)
        except Exception as e:
            log.exception(e)
        self.dbs.get(db_instance_name).put(db)

    def exec_procedures(self, db_instance_name, procedure_name, args_list):
        db = self.dbs.get(db_instance_name).get()
        try:
            with db.cursor() as cursor:
                for args in args_list:
                    cursor.callproc(procedure_name, args)
        except pymysql.OperationalError as e:
            log.exception(e)
            self.dbs.get(db_instance_name).put(self.connect(self.conf.get(db_instance_name)))
            gevent.sleep(3)
            return self.exec_procedures(procedure_name, args_list)
        except Exception as e:
            log.exception(e)
        self.dbs.get(db_instance_name).put(db)

    def __del__(self):
        for dbs_queue in self.dbs.values():
            while not dbs_queue.empty():
                db = dbs_queue.get()
                db.close()


if __name__ == '__main__':
    import gevent.monkey

    gevent.monkey.patch_all()
    import time
    import gevent
    import gevent.pool

    def insert():
        d = {
            'name': 'hello',
            'name2': 'hello',
            'name3': 'hello',
            'name4': 'hello',
            'name5': 'hello',
            'name6': 'hello',
            'name7': 'hello'
        }
        ds = [d for _ in range(100)]
        _start = time.time()
        PyMySQLEx().insert_many('local', 'test', [
            'name', 'name2', 'name3', 'name4', 'name5', 'name6', 'name7',
        ], *ds)
        print(time.time() - _start)

    def select():
        _start = time.time()
        PyMySQLEx().select('local', 'test', ['name', 'name2'], ' name=\'hello\' limit 100')
        print(time.time() - _start)

    PyMySQLEx()

    start = time.time()
    p = gevent.pool.Pool(40)
    for _ in range(10000):
        p.add(gevent.spawn(insert))
    p.join()
    print('>>', time.time() - start)
    while True:
         gevent.sleep(100)
