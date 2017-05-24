# -*- coding: utf-8 -*-
'''
Created on 2017年5月24日

@author: chenyitao
'''

from ..model_base import QuickModelBase


class EventType(object):
    
    NONE = None
    
    class Crawler(object):
    
        BASE_DATA = 1001
        
        COOKIES = 1002
        
        MODULE = 1003
    
    class Parser(object):
        
        BASE_DATA = 2001
    
        MODULE = 2002
    
    class ProxyChecker(object):
    
        BASE_DATA = 3001
        
        MODULE = 3002
        
        SOURCE = 3003
    
    class CookiesGenerator(object):

        BASE_DATA = 4001
        
        MODULE = 4002
    
    class Monitor(object):
    
        BASE_DATA = 5001
        
        MODULE = 5002


class EventBase(QuickModelBase):

    event_type = EventType.NONE
    
    default_values = {'id': None,
                      'timestamp': None,
                      'table': None,
                      'platform': None,
                      'method': None}


def main():
    e = EventBase()
    print(e)

if __name__ == '__main__':
    main()
