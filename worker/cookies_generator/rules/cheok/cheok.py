# -*- coding: utf-8 -*-
'''
Created on 2017年5月22日

@author: chenyitao
'''
import requests
import gevent
from worker.cookies_generator.rules.base import CookiesGeneratorBase

# from ..base import CookiesGeneratorBase


class CheokCookiesGenerator(CookiesGeneratorBase):
    '''
    classdocs
    '''

    EXPRIED = 15

    def run(self):
        gs = []
        for _ in range(10):
            g = gevent.spawn(self._get_cookies)
            gs.append(g)
        gevent.joinall(gs)

    def _get_cookies(self):
        rsp = requests.get('http://www.cheok.com/car/cp_1')
        cookie = [k+'='+v for k, v in zip(rsp.cookies.keys(), rsp.cookies.values())]
        self._cookies.append(cookie)

        
def main():
    print(CheokCookiesGenerator().cookies)
    while True:
        gevent.sleep(10)

if __name__ == '__main__':
    main()
