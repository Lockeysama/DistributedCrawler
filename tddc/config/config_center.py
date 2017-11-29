# -*- coding: utf-8 -*-
"""
Created on 2017年8月31日

@author: chenyitao
"""

import sqlite3
from string import capitalize

from ..log.logger import TDDCLogger
from ..util.util import Singleton


class ConfigCenter(TDDCLogger):
    """
    classdocs
    """
    __metaclass__ = Singleton

    def __init__(self):
        """
        Constructor
        """
        super(ConfigCenter, self).__init__()
        self._connection = sqlite3.connect("./config.sqlite3")
        self._init_table()

    @staticmethod
    def tables():
        return {}

    def _init_table(self):
        tables = self.tables()
        for table, fields in tables.items():
            table_fields = self._connection.execute("PRAGMA table_info(\"%s\");" % table).fetchall()
            table_fields = [field_info[1] for field_info in table_fields]
            if table_fields:
                keys = fields.keys()
                if set(table_fields) == set(keys):
                    continue
                self._connection.execute("DROP TABLE IF EXISTS `%s_new`;" % table)
                self._create_table(table + '_new', fields)
                self._connection.execute("DELETE FROM `%s` WHERE _rowid_!=0;" % table)
                _fields = [field for field in keys if field in table_fields]
                self._connection.execute(("INSERT INTO `%s_new`(%s) "
                                          "SELECT %s FROM `%s`;" % (table,
                                                                    ','.join(_fields),
                                                                    ','.join(_fields),
                                                                    table)))
                self._connection.execute("DROP TABLE `%s`" % table)
                self._connection.execute("ALTER TABLE `%s_new` RENAME TO `%s`;" % (table, table))
                continue
            self._create_table(table, fields)

    def _create_table(self, table, fields):
        create_sql = "CREATE TABLE `{table_name}` (".format(table_name=table)
        insert_sql = "INSERT INTO `{table_name}` (".format(table_name=table)
        default_str = ""
        for field, field_attr in fields.items():
            _type = field_attr.get('field_type', 'TEXT')
            default = field_attr.get('default_value', '')
            if _type == 'TEXT':
                default = "'%s'" % default
            create_sql += "`{field_name}`    {type},".format(field_name=field,
                                                             type=_type)
            insert_sql += "`{field_name}`,".format(field_name=field)
            default_str += "{value},".format(value=default)
        create_sql = create_sql[:-1] + ');'
        self._connection.execute(create_sql)
        if default_str.strip('\',') != '':
            insert_sql = insert_sql[:-1] + ") VALUES ({values});".format(values=default_str[:-1])
            self._connection.execute(insert_sql)
        self._connection.commit()

    def _get_info(self, table):
        keys = self.tables().get(table).keys()
        sql = "SELECT %s FROM `%s`;" % (','.join(keys), table)
        info = self._connection.execute(sql).fetchall()
        if not info:
            return None
        obj = type(str(capitalize(table)) + 'Info',
                   (),
                   {keys[i]: info[0][i] for i in range(len(keys))})
        return obj
