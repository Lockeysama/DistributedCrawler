# -*- coding: utf-8 -*-
'''
Created on 2017年4月14日

@author: chenyitao
'''

import gevent.queue

from ..log.logger import TDDCLogger
from ..util.util import Singleton
from ..hbase.hbase import HBaseManager


class Storager(TDDCLogger):
    '''
    classdocs
    '''
    __metaclass__ = Singleton

    def __init__(self):
        super(Storager, self).__init__()
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
                HBaseManager().put(data.table, data.row_key, data.data)
            except Exception as e:
                self.exception(e)
            else:
                callable(callback(data))
