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
        self._create_table()

    @staticmethod
    def tables():
        return {"worker": {"id": "TEXT",
                           "name": "TEXT",
                           "config_online_source": "TEXT"},
                "service": {"server_name": "TEXT",
                            "host": "TEXT",
                            "port": "TEXT"},
                "event": {"topic": "TEXT",
                          "group_id": "TEXT"},
                "exception": {"topic": "TEXT",
                              "group_id": "TEXT"},
                "extern_modules": {"platform": "TEXT",
                                   "package": "TEXT",
                                   "mould": "TEXT",
                                   "feature": "TEXT",
                                   "version": "TEXT",
                                   "md5": "TEXT",
                                   "valid": "BLOB",
                                   "update_time": "TEXT"}
                }

    def _create_table(self):
        check_sql = ("SELECT count(*) FROM `sqlite_master` "
                     "WHERE type=\"table\" AND name=\"{table_name}\";")
        for table, fields in self.tables().items():
            if self._connection.execute(check_sql.format(table_name=table)).fetchall()[0][0] == 1:
                return
            create_sql = "CREATE TABLE `{table_name}` (".format(table_name=table)
            for field, _type in fields.items():
                create_sql += "`{field_name}`    {type},".format(field_name=field, type=_type)
            create_sql += "`{field_name}`    {type},".format(field_name='describe', type='TEXT')
            create_sql = create_sql[:-1] + ');'
            self._connection.execute(create_sql)
            self._connection.commit()

    def get_worker(self):
        return self._get_info('worker')

    def get_event(self):
        return self._get_info('event')

    def get_exception(self):
        return self._get_info('exception')

    def get_services(self, server_name=None):
        keys = self.tables().get("service").keys()
        sql = "SELECT %s FROM `service`" % ','.join(keys)
        sql += ";" if not server_name else " WHERE server_name=\"%s\";" % server_name
        servers = self._connection.execute(sql).fetchall()
        conf = {}
        for service in servers:
            server_name = service[keys.index('server_name')]
            if not conf.get(server_name):
                conf[server_name] = []
            packages = conf.get(server_name, [])
            obj = type(str(capitalize(server_name)) + 'ServerInfo',
                       (),
                       {keys[i]: service[i] for i in range(len(keys))})
            packages.append(obj)
        return conf if conf else None

    def get_extern_modules(self, platform=None):
        keys = self.tables().get("extern_modules").keys()
        sql = "SELECT %s FROM `extern_modules` WHERE valid=\"1\"" % ','.join(keys)
        sql += ";" if not platform else " AND platform=\"%s\";" % platform
        extern_modules = self._connection.execute(sql).fetchall()
        conf = {}
        for extern_module in extern_modules:
            platform = extern_module[keys.index('platform')]
            if not conf.get(platform):
                conf[platform] = []
            packages = conf.get(platform, [])
            obj = type(str(extern_module[keys.index('mould')]) + 'ExternModuleInfo',
                       (),
                       {keys[i]: extern_module[i] for i in range(len(keys))})
            packages.append(obj)
        return conf if conf else None

    def set_extern_modules(self, platform, packages):
        def _insert(self, platform, package):
            sql_fmt = ("INSERT INTO `extern_modules`"
                       "(`platform`,`package`,`mould`,`feature`,`version`,`md5`,`valid`,`update_time`) "
                       "VALUES (\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",%d,datetime());")
            sql = sql_fmt % (platform,
                             package.package,
                             package.mould,
                             package.feature,
                             package.version,
                             package.md5,
                             package.valid)
            self._connection.execute(sql)
            self._connection.commit()

        def _update(self, platform, package):
            sql_fmt = ("UPDATE `extern_modules` "
                       "SET `version`=\"%s\", `md5`=\"%s\", `update_time`=datetime() "
                       "WHERE `feature`=\"%s\" AND `platform`=\"%s\";")
            sql = sql_fmt % (package.version,
                             package.md5,
                             package.feature,
                             platform)
            self._connection.execute(sql)
            self._connection.commit()

        sql_fmt = "SELECT * FROM `extern_modules` WHERE feature=\"%s\";"
        for package in packages:
            sql = sql_fmt % package.feature
            ret = self._connection.execute(sql)
            if len(ret.fetchall()):
                _update(self, platform, package)
            else:
                _insert(self, platform, package)

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
