# -*- coding: utf-8 -*-
'''
Created on 2017年8月31日

@author: chenyitao
'''

import sqlite3


class ConfigCenter(object):
    '''
    classdocs
    '''


    def __init__(self, db_path):
        '''
        Constructor
        '''
        self._sqlite3_connection = sqlite3.connect(db_path)
        self.create_table()

    def create_table(self):
        check_sql = ("select count(*) from sqlite_master "
                     "where type='table' and name='extern_modules';")
        if self._sqlite3_connection.execute(check_sql).fetchall()[0][0] == 1:
            return
        sql = ('CREATE TABLE `extern_modules` ('
                '`platform`    TEXT,'
                '`package`    TEXT,'
                '`mould`    TEXT,'
                '`version`    TEXT,'
                '`md5`    TEXT,'
                '`valid`    BLOB'
                ');')
        self._sqlite3_connection.execute(sql)
        self._sqlite3_connection.commit()

    def load_extern_modules_conf(self):
        sql = 'SELECT * FROM extern_modules;'
        extern_modules = self._sqlite3_connection.execute(sql).fetchall()
        conf = {}
        for extern_module in extern_modules:
            keys = ('package', 'mould', 'version', 'md5', 'valid')
            platform = extern_module[0]
            info = extern_module[1:]
            if not conf.get(platform):
                conf[platform] = []
            packages = conf.get(platform, [])
            packages.append({keys[i]: info[i] for i in range(len(keys))})
        return conf

    def update_extern_modules_conf(self, platform, packages):
        sql_fmt = ("INSERT INTO `extern_modules`"
                   "(`platform`,`package`,`mould`,`version`,`md5`,`valid`) "
                   "VALUES ('%s','%s','%s','%s','%s',%d);")
        for package in packages:
            sql = sql_fmt % (platform,
                             package.get('package'),
                             package.get('mould'),
                             package.get('version'),
                             package.get('md5'),
                             package.get('valid', 1))
            self._sqlite3_connection.execute(sql)
            self._sqlite3_connection.commit()
