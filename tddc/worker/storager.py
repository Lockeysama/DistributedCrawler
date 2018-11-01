# -*- coding: utf-8 -*-
'''
Created on 2017年4月14日

@author: chenyitao
'''
import logging

import gevent.queue

from ..base.util import Singleton
from ..base.hbase import HBaseManager
from ..base.mongodb import MongoDBManager

from online_config import OnlineConfig

log = logging.getLogger(__name__)


class Storager(object):
    '''
    存储管理、目前支持HBase、MongoDB
    '''
    __metaclass__ = Singleton

    def __init__(self):
        log.info('Storager Is Starting.')
        self.hbase = None
        self._q_hbase = gevent.queue.Queue()
        gevent.spawn(self._storage_to_hbase)
        gevent.sleep()
        self.mongo = None
        self._q_mongo = gevent.queue.Queue()
        gevent.spawn(self._storage_to_mongo)
        gevent.sleep()
        super(Storager, self).__init__()
        log.info('Storager Was Started.')

    @property
    def hbase_status(self):
        if not self.hbase:
            return type('HBaseStatus', (), {'alive_timestamp': -1})()
        return self.hbase.get_connection_status() \
            if self.hbase \
            else type('HBaseStatus', (), {'alive_timestamp': -1})()

    @property
    def mongo_status(self):
        if not self.mongo:
            return type('MongoStatus', (), {'alive_timestamp': -1})()
        return self.mongo.get_connection_status() \
            if self.mongo \
            else type('MongoStatus', (), {'alive_timestamp': -1})()

    def storage_to_hbase(self, data, callback=None):
        self._q_hbase.put((data, callback))

    def _storage_to_hbase(self):
        while True:
            (data, callback) = self._q_hbase.get()
            data = type('Data', (), data)
            try:
                if not self.hbase:
                    self.hbase = HBaseManager(OnlineConfig().hbase)
                self.hbase.put(data.table, data.row_key, data.data)
            except Exception as e:
                log.exception(e)
                if data and hasattr(data, 'table') and hasattr(data, 'row_key'):
                    self._q_hbase.put((data, callback))
            else:
                log.debug('[%s:%s] Storaged.' % (data.table, data.row_key))
                callable(callback(data))

    def storage_to_mongo(self, db, table, data, callback=None):
        self._q_mongo.put((db, table, data, callback))

    def _storage_to_mongo(self):
        while True:
            (db, table, data, callback) = self._q_mongo.get()
            try:
                if not self.mongo:
                    self.mongo = MongoDBManager(OnlineConfig().mongodb)
                self.mongo.insert(db, table, data)
            except Exception as e:
                if 'auth':
                    self.mongo[db].authenticate(
                        OnlineConfig().mongodb.get(db).user,
                        OnlineConfig().mongodb.get(db).password
                    )
                    log.warning('auth')
                log.exception(e)
                if db and table and data and isinstance(data, list):
                    self._q_mongo.put((db, table, data, callback))
            else:
                log.debug('[%s:%s] Storaged(%s).' % (db, table, len(data)))
                if callback:
                    callback(data)
