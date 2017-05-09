# -*- coding: utf-8 -*-
'''
Created on 2017年5月8日

@author: chenyitao
'''

import gevent

from plugins.db.db_manager import DBManager


class StoragerBase(object):
    '''
    classdocs
    '''

    def __init__(self, tag=''):
        '''
        Constructor
        '''
        print('-->Storager Manager Is Starting.')
        self._db = DBManager(tag)
        gevent.spawn(self._push)
        gevent.sleep()
        gevent.spawn(self._pull)
        gevent.sleep()
        print('-->Storager Manager Was Ready.')

    def _push(self):
        pass
    
    def _pull(self):
        pass


def main():
    pass

if __name__ == '__main__':
    main()
