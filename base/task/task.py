# -*- coding: utf-8 -*-
'''
Created on 2017年4月7日

@author: chenyitao
'''

import random

class Task(object):

    class Status(object):
        DEFAULT = 0
        WAIT_CRAWL = 0
        CRAWL_SUCCESS = 1
        CRAWL_FAILED = 2
        WAIT_PARSE = 3
        PARSE_SUCCESS = 4
        PARSE_FAILED = 5
        WAIT_STORAGE = 6
        STORAGE_SUCCESS = 7
        STORAGE_FAILED = 8

    @staticmethod
    def id_generator(size=16, chars='qwertyuiopasdfghjklllzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890'):
        return ''.join(random.choice(chars) for _ in range(size))

    def __init__(self, task_info_dict=None):
        self.id = None
        self.platform = 'unknow'
        self.row_key = 'unkonw'
        self.type = 'unknow'
        self.status = Task.Status.DEFAULT
        self.feature = None
        self.url = None
        if task_info_dict is not None and isinstance(task_info_dict, dict):
            self.id = task_info_dict.get('id', None)
            self.platform = task_info_dict.get('platform', 'unknow')
            self.row_key = task_info_dict.get('row_key', 'unknow')
            self.type = task_info_dict.get('type', 'unknow')
            self.url = task_info_dict.get('url')
            self.feature = task_info_dict.get('feature', None)


class StorageTask(Task):

    def __init__(self, task=None, atorage_info_dict=None):
        super(StorageTask, self).__init__(atorage_info_dict)
        self.status = Task.Status.WAIT_STORAGE
        if task is not None:
            self.id = task.id
            self.url = task.url
            self.type = task.type
        if atorage_info_dict is not None and type(atorage_info_dict) == dict:
            self.item = atorage_info_dict.get('item')
            return
        self.item = None


def main():
    pass
#     crawl_task = CrawlTask({'url': 'http://www.chenyitao.com', 'ip': '192.168.1.100'})
#     print(crawl_task.url, crawl_task.ip, crawl_task.id, crawl_task.status)
#     storage_task = StorageTask(parser_task, {'item': ['hello', 'world']})
#     print(storage_task.url, storage_task.id, storage_task.status, storage_task.item)

if __name__ == '__main__':
    main()
