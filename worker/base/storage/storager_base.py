# -*- coding: utf-8 -*-
'''
Created on 2017年5月8日

@author: chenyitao
'''

import gevent

from common import TDDCLogging
from conf.default import HBaseSite

from plugins import DBManager


class StoragerBase(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        TDDCLogging.info('-->Storager Manager Is Starting.')
        self._db = DBManager(HBaseSite.random_hbase_node())
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
