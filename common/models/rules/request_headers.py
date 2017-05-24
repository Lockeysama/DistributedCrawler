# -*- coding: utf-8 -*-
'''
Created on 2017年5月24日

@author: chenyitao
'''

from .rules_base import QuickModelBase


class RequestHeadersRules(QuickModelBase):
    '''
    classdocs
    '''

    default_values = {'platform': None,
                      'Proxy': None,
                      'Host': None,
                      'User-Agent': None,
                      'Accept': None,
                      'Accept-Encoding': None,
                      'Accept-Language': None,
                      'Cookie': None,
                      'Referer': None,
                      'Cache-Control': None,
                      'Connection': None,
                      'DNT': None,
                      'Upgrade-Insecure-Requests': None,
                      'X-Requested-With': None,
                      'post_params': None}

        
def main():
    pass

if __name__ == '__main__':
    main()
