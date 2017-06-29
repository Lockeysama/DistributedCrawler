# -*- coding: utf-8 -*-
'''
Created on 2017年4月18日

@author: chenyitao
'''

import hashlib
from lxml import html
import json


class ParseRuleBase(object):
    '''
    classdocs
    '''
    
    JSON = 'JSON'
    
    HTML = 'HTML'

    platform = ''

    feature = ''
    
    version = 'unknow'

    def __init__(self, task, body):
        '''
        Constructor
        '''
        self.platform
        self._task = task
        self._body = body
        self._body_type = None
        self.items = dict()
        self.tasks = list()
        self._md5_mk = hashlib.md5()
        if body[0] == '{' and body[-1] == '}' or body[0] == '[' and body[-1] == ']':
            try:
                self._json_dict = json.loads(body)
            except Exception, e:
                print(e)
            else:
                self._body_type = self.JSON
        else:
            self._doc = html.document_fromstring(body)
            self._body_type = self.HTML
        self._parse()
        
    def _parse(self):
        pass
    
    def _xpath(self, xp):
        if self._body_type == self.HTML:
            return self._doc.xpath(xp)
        return None
    
    def _get(self, key, default=None):
        if self._body_type == self.JSON:
            return self._json_dict.get(key, default)
        return None


def main():
    pass
    
if __name__ == '__main__':
    main()
