# -*- coding: utf-8 -*-
'''
Created on 2017年5月22日

@author: chenyitao
'''
import time

class CookiesGeneratorBase():

    EXPRIED = 60 * 60 * 24

    def __init__(self):
        '''
        Constructor
        '''
        self._cookies = []
        self.run()
        
    def run(self):
        pass
    
    @property
    def cookies(self):
        return time.time(), self._cookies


def main():
    pass

if __name__ == '__main__':
    main()
