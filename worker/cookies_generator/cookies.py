# -*- coding: utf-8 -*-
'''
Created on 2017年5月22日

@author: chenyitao
'''

from plugins import RedisClient
import gevent

class CookiesManager(RedisClient):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        gevent.spawn(self._upload_cookies_to_remote)
        gevent.sleep()

    def _upload_cookies_to_remote(self):
        while True:
            gevent.sleep(10)


def main():
    pass

if __name__ == '__main__':
    main()
