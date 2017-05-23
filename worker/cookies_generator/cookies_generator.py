# -*- coding: utf-8 -*-
'''
Created on 2017年5月22日

@author: chenyitao
'''

import gevent
import time
import json

from common import TDDCLogging
from worker.cookies_generator.rules.cheok.cheok import CheokCookiesGenerator



class CookiesGenerator(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self._generators = {'cheok': [0, CheokCookiesGenerator]}
        gevent.spawn(self._generator)
        gevent.sleep()

    def _generator(self):
        cookies_info = {}
        while True:
            TDDCLogging.debug('Generating.')
            cur_time = time.time()
            for platform, (pre_time, cls) in self._generators.items():
                if cur_time - pre_time > cls.EXPRIED:
                    TDDCLogging.debug('Generating Cookies [%s].' % platform)
                    cookies_info[platform] = cls().cookies
                    self._generators[platform][0] = cur_time
                    TDDCLogging.debug('Generated Cookies [%s].' % platform)
                    TDDCLogging.debug(json.dumps(cookies_info))
            TDDCLogging.debug('Generated.')
            gevent.sleep(5)

        
def main():
    CookiesGenerator()
    while True:
        gevent.sleep(10)

if __name__ == '__main__':
    main()
