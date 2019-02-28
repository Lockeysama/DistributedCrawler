# -*- coding: utf-8 -*-
"""
Created on 2017年4月14日

@author: chenyitao
"""
import logging

import gevent.queue
import six

from ..base.util import Singleton
from ..base.mongodb import MongoDBManager

from .online_config import OnlineConfig

log = logging.getLogger(__name__)


@six.add_metaclass(Singleton)
class Storager(object):
    """
    存储管理、目前支持HBase、MongoDB
    """

    def __init__(self):
        log.info('Storager Is Starting.')
        self.mongo = None
        self._q_mongo = gevent.queue.Queue()
        gevent.spawn(self._storage_to_mongo)
        gevent.sleep()
        super(Storager, self).__init__()
        log.info('Storager Was Started.')

    def mongodb(self, db):
        try:
            if not self.mongo:
                self.mongo = MongoDBManager(OnlineConfig().mongodb)
                self.mongo[db].authenticate(
                    OnlineConfig().mongodb.get(db).user,
                    OnlineConfig().mongodb.get(db).password
                )
        except Exception as e:
            log.exception(e)
            self.mongo[db].authenticate(
                OnlineConfig().mongodb.get(db).user,
                OnlineConfig().mongodb.get(db).password
            )
        finally:
            return self.mongo[db]

    @property
    def mongo_status(self):
        if not self.mongo:
            return type('MongoStatus', (), {'alive_timestamp': -1})()
        return self.mongo.get_connection_status() \
            if self.mongo \
            else type('MongoStatus', (), {'alive_timestamp': -1})()

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
