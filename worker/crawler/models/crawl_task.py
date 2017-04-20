# -*- coding: utf-8 -*-
'''
Created on 2017年4月14日

@author: chenyitao
'''

from base.task.task import Task

class CrawlTask(Task):

    def __init__(self, info_dict=None):
        super(CrawlTask, self).__init__(info_dict)
        self.id = Task.id_generator()
        self.cookie = None
        self.ip = None
        self.ua = None
        self.method = 'GET'
        self.proxy_type = 'http'
        if info_dict is not None and type(info_dict) == dict:
            self.cookie = info_dict.get('cookie')
            self.ip = info_dict.get('ip')
            self.ua = info_dict.get('ua')
            self.method = info_dict.get('method', 'GET')
            self.proxy_type = info_dict.get('proxy_type', 'http')
       

def main():
    pass
    
if __name__ == '__main__':
    main()
