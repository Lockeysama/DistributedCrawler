# -*- coding: utf-8 -*-
'''
Created on 2017年4月14日

@author: chenyitao
'''

import gevent

from conf.base_site import PLATFORM_SUFFIX
from common.queues import STORAGE_QUEUE, PARSE_QUEUE

from . import StoragerBase


class CrawlStorager(StoragerBase):
    '''
    classdocs
    '''
        
    def _push(self):
        while True:
            try:
                task, rsp_info = STORAGE_QUEUE.get()
                items = {'source': rsp_info,
                         'task': {'task': task.to_json()}}
                if self._db.put_to_hbase(task.platform + PLATFORM_SUFFIX, task.row_key, items):
                    PARSE_QUEUE.put((task, rsp_info.get('rsp')[1] if rsp_info.get('rsp') else None))
                else:
                    STORAGE_QUEUE.put((task, rsp_info))
                    gevent.sleep(1)
            except Exception, e:
                print(e)


def main():
    CrawlStorager()
    while True:
        gevent.sleep()

if __name__ == '__main__':
    main()
