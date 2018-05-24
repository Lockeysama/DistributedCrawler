# -*- coding: utf-8 -*-
'''
Created on 2017年4月14日

@author: chenyitao
'''
import logging

import gevent.queue
from .models import MongoModel, HBaseModel, DBSession

from ..util.util import Singleton
from ..hbase.hbase import HBaseManager
from ..mongodb.mongodbm import MongoDBManager

log = logging.getLogger(__name__)


class Storager(object):
    '''
    存储管理、目前支持HBase、MongoDB
    '''
    __metaclass__ = Singleton

    def __init__(self):
        log.info('Storager Is Starting.')
        hbase_nodes = DBSession.query(HBaseModel).all()
        if not hbase_nodes:
            self.hbase = None
            log.warning('>>> HBase Nodes Not Found.')
        else:
            self.hbase = HBaseManager(hbase_nodes)
            self._q_hbase = gevent.queue.Queue()
            gevent.spawn(self._storage_to_hbase)
            gevent.sleep()
        mongo_nodes = DBSession.query(MongoModel).all()
        if not mongo_nodes:
            self.mongo = None
            log.warning('>>> MongoDB Nodes Not Found.')
        else:
            self.mongo = MongoDBManager(mongo_nodes)
            self._q_mongo = gevent.queue.Queue()
            gevent.spawn(self._storage_to_mongo)
            gevent.sleep()
        super(Storager, self).__init__()
        if not hbase_nodes and not mongo_nodes:
            log.warning('Storager Start Failed.')
            return
        log.info('Storager Was Started.')

    @property
    def hbase_status(self):
        return self.hbase.get_connection_status() \
            if self.hbase \
            else type('HBaseStatus', (), {'alive_timestamp': -1})()

    @property
    def mongo_status(self):
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
                self.mongo.insert(db, table, data)
            except Exception as e:
                log.exception(e)
                if db and table and data and isinstance(data, list):
                    self._q_mongo.put((db, table, data, callback))
            else:
                log.debug('[%s:%s] Storaged(%s).' % (db, table, len(data)))
                if callback:
                    callback(data)
