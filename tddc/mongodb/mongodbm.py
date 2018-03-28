# -*- coding: utf-8 -*-
'''
Created on 2017年4月10日

@author: chenyitao
'''
import logging
import random

import gevent
import pymongo
import time
from bson.objectid import ObjectId

log = logging.getLogger(__name__)


class MongoDBManager(pymongo.MongoClient):

    def __init__(self, nodes):
        if not nodes:
            log.info('MongoDB Node Not Found.')
            return
        self._nodes = nodes
        self._current_node = random.choice(self._nodes)
        super(MongoDBManager, self).__init__(self._current_node.host,
                                             self._current_node.port)
        self.status = type('MongoDBStatus', (), {'alive_timestamp': 0})
        gevent.spawn(self._alive_check)
        gevent.sleep()

    def _alive_check(self):
        while True:
            if not self['local']:
                gevent.sleep(5)
                continue
            self.status.alive_timestamp = int(time.time())
            gevent.sleep(5)

    def get_connection_status(self):
        return self.status

    def insert(self, db, table, docs):
        return self[db][table].insert_many(docs)

    def delete(self, db, table, query):
        return self[db][table].delete_many(query)

    def delete_with_id(self, db, table, oid):
        return self[db][table].delete_many({'_id': ObjectId(oid)})

    def update(self, db, table, docs, query=None):
        return self[db][table].update_many(filter=query, update=docs)

    def find_one(self, db, table, query=None):
        return self[db][table].find_one(query)

    def find_one_with_id(self, db, table, oid):
        return self[db][table].find_one({'_id': ObjectId(oid)})

    def find_all(self, db, table, query=None):
        return self[db][table].find(query)
