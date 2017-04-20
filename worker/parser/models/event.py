# -*- coding: utf-8 -*-
'''
Created on 2017年4月13日

@author: chenyitao
'''

class Event(object):
    '''
    classdocs
    '''

    def __init__(self, task_info_dict=None):
        '''
        Constructor
        '''
        self.id = None
        self.type = None
        self.platform = None
        if task_info_dict is not None and isinstance(task_info_dict, dict):
            self.id = task_info_dict.get('id', None)
            self.type = task_info_dict.get('type', None)
            self.platform = task_info_dict.get('platform', None)


def main():
    pass

if __name__ == '__main__':
    main()