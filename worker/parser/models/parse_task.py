# -*- coding: utf-8 -*-
'''
Created on 2017年4月12日

@author: chenyitao
'''
from common.models.task import Task

class ParseTask(Task):

    def __init__(self, task=None, parse_info_dict=None):
        _dict = {}
        if task:
            _dict.update(task.__dict__)
        if isinstance(parse_info_dict, dict):
            _dict.update(parse_info_dict)
        super(ParseTask, self).__init__(_dict)
        self.status = Task.Status.WAIT_PARSE
        self.body = _dict.get('body', None)


def main():
    pass

if __name__ == '__main__':
    main()