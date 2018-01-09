# -*- coding: utf-8 -*-
'''
Created on 2017年4月14日

@author: chenyitao
'''

import gevent.queue

from ..util.util import Singleton
from ..hbase.hbase import HBaseManager

from .worker_config import WorkerConfigCenter


class Storager(HBaseManager):
    '''
    classdocs
    '''
    __metaclass__ = Singleton

    def __init__(self):
        nodes = WorkerConfigCenter().get_hbase()
        if not nodes:
            print('>>> HBase Nodes Not Found.')
            return
        super(Storager, self).__init__(nodes)
        self.info('Storager Is Starting.')
        self._q = gevent.queue.Queue()
        gevent.spawn(self._storage)
        gevent.sleep()
        self.info('Storager Was Started.')

    def storage(self, data, callback=None):
        self._q.put((data, callback))

    def _storage(self):
        while True:
            (data, callback) = self._q.get()
            data = type('Data', (), data)
            try:
                self.put(data.table, data.row_key, data.data)
            except Exception as e:
                self.exception(e)
                if data and hasattr(data, 'table') and hasattr(data, 'row_key'):
                    self._q.put((data, callback))
            else:
                self.debug('[%s:%s] Storaged.' % (data.table, data.row_key))
                callable(callback(data))
