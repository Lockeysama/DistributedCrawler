# -*- coding: utf-8 -*-
'''
Created on 2017年5月22日

@author: chenyitao
'''

import gevent
import setproctitle

from log import TDDCLogging


class CookiesGeneratorManager(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        setproctitle.setproctitle("TDDC_CRAWLER")
        TDDCLogging.info('->Crawler Starting.')
        
        TDDCLogging.info('->Crawler Was Ready.')

    @staticmethod
    def start():
        while True:
            gevent.sleep(15)


def main():
    pass

if __name__ == '__main__':
    main()
