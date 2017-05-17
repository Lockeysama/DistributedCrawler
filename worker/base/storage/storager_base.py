# -*- coding: utf-8 -*-
'''
Created on 2017年5月8日

@author: chenyitao
'''

import gevent

from plugins import DBManager
from common import TDDCLogging
from conf.base_site import HBASE_HOST_PORT


class StoragerBase(object):
    '''
    classdocs
    '''

    def __init__(self, tag=''):
        '''
        Constructor
        '''
        TDDCLogging.info('-->Storager Manager Is Starting.')
        self._db = DBManager(tag, HBASE_HOST_PORT)
        gevent.spawn(self._push)
        gevent.sleep()
        gevent.spawn(self._pull)
        gevent.sleep()
        TDDCLogging.info('-->Storager Manager Was Ready.')

    def _push(self):
        pass
    
    def _pull(self):
        pass


def main():
    pass

if __name__ == '__main__':
    main()
