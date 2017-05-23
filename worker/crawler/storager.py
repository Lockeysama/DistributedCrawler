# -*- coding: utf-8 -*-
'''
Created on 2017年4月14日

@author: chenyitao
'''

import gevent

from conf.base_site import PLATFORM_SUFFIX
from common.queues import CrawlerQueues

from . import StoragerBase
from common.models import Task
import json


class CrawlStorager(StoragerBase):
    '''
    classdocs
    '''
        
    def _push(self):
        cnt = 0
        platform_rows = {}
        while True:
            try:
                task, rsp_info = CrawlerQueues.STORAGE.get()
                items = {'source': rsp_info,
                         'task': {'task': task.to_json()}}
                if not platform_rows.get(task.platform + PLATFORM_SUFFIX):
                    platform_rows[task.platform + PLATFORM_SUFFIX] = {}
                platform_rows[task.platform + PLATFORM_SUFFIX][task.row_key] = items
                cnt += 1
                gevent.sleep(0.05)
                if CrawlerQueues.STORAGE.qsize() or not cnt % 5:
                    continue
                if self._db.puts_to_hbase(platform_rows):
                    self._pushed(platform_rows, True)
                else:
                    self._pushed(platform_rows, False)
                    gevent.sleep(1)
                platform_rows = {}
            except Exception, e:
                print(e)

    def _pushed(self, platform_rows, success):
        for _, rows in platform_rows.items():
            for _, row in rows.items():
                rsp_info = row.get('source')
                task = Task(**json.loads(row.get('task').get('task')))
                if success:
                    CrawlerQueues.PARSE.put((task, rsp_info.get('rsp')[1] if rsp_info.get('rsp') else None))
                else:
                    CrawlerQueues.STORAGE.put((task, rsp_info))


def main():
    CrawlStorager()
    while True:
        gevent.sleep()

if __name__ == '__main__':
    main()
