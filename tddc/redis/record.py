# -*- coding: utf-8 -*-
'''
Created on 2017年5月8日

@author: chenyitao
'''

import gevent

from .redis_client import RedisClient


class RecordManager(RedisClient):
    '''
    classdocs
    '''

    def create_record(self, name, key, record):
        times = 0
        while True:
            try:
                self.hset(name, key, record)
            except Exception as e:
                self.exception(e)
                gevent.sleep(1)
                times += 1
                if times == 5:
                    self.error('Create Record [%s:%s:%s] Failed.'.format(name, key, record))
                    break
            else:
                break

    def get_record(self, name, key, callback, **kwargs):
        times = 0
        while True:
            try:
                record = self.hget(name, key)
            except Exception as e:
                self.exception(e)
                gevent.sleep(0.5)
                times += 1
                if times == 5:
                    self.error('Get Record [%s:%s] Failed.'.format(name, key))
                    break
            else:
                callback(record, **kwargs)
                break
