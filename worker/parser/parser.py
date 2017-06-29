# -*- coding: utf-8 -*-
'''
Created on 2017年4月11日

@author: chenyitao
'''

import gevent

from common import TDDCLogging
from common.queues import ParserQueues
from .parser_moulds.manager import ParsePackagesManager


class Parser(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        TDDCLogging.info('-->Parser Is Starting.')
        self._rules_updater = ParsePackagesManager()
        gevent.spawn(self._parse)
        gevent.sleep()
        TDDCLogging.info('-->Parser Was Ready.')

    def _parse(self):
        while True:
            task, body = ParserQueues.WAITING_PARSE.get()
            cls = self._rules_updater.get_parse_model(task.platform, task.feature)
            if not cls:
                fmt = 'Parse No Match: [P:{platform}][F:{feature}][K:{row_key}]'
                TDDCLogging.warning(fmt.format(platform=task.platform,
                                               feature=task.feature,
                                               row_key=task.row_key))
                continue
            try:
                ret = cls(task, body)
            except Exception, e:
                TDDCLogging.error(e)
                continue
            self._storage(task, ret.items)
            self._new_task_push(ret.tasks)
            fmt = 'Parsed: [{platform}:{row_key}:{feature}][S:{items}][N:{tasks}]'
            TDDCLogging.info(fmt.format(platform=task.platform,
                                        feature=task.feature,
                                        row_key=task.row_key,
                                        items=len(ret.items),
                                        tasks=len(ret.tasks)))
            ParserQueues.TASK_STATUS.put(task)

    @staticmethod
    def _storage(task, items):
        if len(items):
            ParserQueues.STORAGE.put([task, items])
    
    @staticmethod
    def _new_task_push(tasks):
        for task in tasks:
            ParserQueues.CRAWL.put(task)
    
    
def main():
    from common.models import Task
    Parser()
    cnt = 100
    gevent.sleep(3)
    while True:
        if cnt > 0:
            parser_task = Task(parse_info_dict={'id': '%d' % cnt, 'status': 3, 'body': 'hello'})
            ParserQueues.WAITING_PARSE.put(parser_task)
            cnt -= 1
            if cnt == 0:
                print('Done')
        gevent.sleep(0.01)
    

if __name__ == '__main__':
    main()