# -*- coding: utf-8 -*-
'''
Created on 2017年4月12日

@author: chenyitao
'''

import json

import gevent

from base import BloomFilter, TaskManagerBase
from base.plugins import KafkaHelper
from common import TDDCLogging
from common.models import Task
from common.queues import ParserQueues
from conf import ParserSite


class ParseTaskManager(TaskManagerBase):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        TDDCLogging.info('-->Task Manager Is Starting.')
        super(ParseTaskManager, self).__init__()
        self._filter = BloomFilter()
        self._start_mq_server()
        TDDCLogging.info('-->Task Manager Was Ready.')

    def _start_mq_server(self):
        self._consumer = KafkaHelper.make_consumer(ParserSite.KAFKA_NODES,
                                                   ParserSite.PARSE_TOPIC,
                                                   ParserSite.PARSE_TOPIC_GROUP)
        gevent.spawn(self._fetch)
        gevent.sleep()
        gevent.spawn(self._push_new_crawl_task)
        gevent.sleep()
        gevent.spawn(self._task_status_update)
        gevent.sleep()

    def _fetch(self):
        TDDCLogging.info('--->Parsing Task Consumer Was Ready.')
        pause = False
        while True:
            if ParserQueues.PARSE.qsize() > ParserSite.FETCH_SOURCE_CONCURRENT * 4:
                if not pause:
                    self._consumer.commit()
                    self._consumer.unsubscribe()
                    pause = True
                    TDDCLogging.info('Parsing Task Consumer Was Paused.')
                gevent.sleep(1)
                continue
            if pause:
                self._consumer.subscribe(ParserSite.PARSE_TOPIC)
                pause = False
                TDDCLogging.info('Parsing Task Consumer Was Resumed.')
            partition_records = self._consumer.poll(2000, 16)
            if not len(partition_records):
                gevent.sleep(1)
                continue
            for _, records in partition_records.items():
                for record in records:
                    self._record_proc(record)
    
    def _record_proc(self, record):
        try:
            item = json.loads(record.value)
        except Exception, e:
            self._consume_msg_exp('PARSE_TASK_JSON_ERR', record.value, e)
        else:
            if item and isinstance(item, dict) and item.get('url', None):
                task = Task(**item)
                task.status = Task.Status.WAIT_PARSE
                ParserQueues.PARSE.put(task)
                ParserQueues.TASK_STATUS.put(task)
            else:
                self._consume_msg_exp('PARSE_TASK_ERR', item)

    def _push_new_crawl_task(self):
        TDDCLogging.info('--->Parser Task Producer Was Ready.')
        while True:
            task = ParserQueues.CRAWL.get()
#             if not self._filter.setget(task.url):
#                 TDDCLogging.debug('New Task [%s:%s] Was Filter.' % (task.platform, task.url))
#                 continue
            msg = json.dumps(task.__dict__)
            if msg:
                self._push_task(ParserSite.CRAWL_TOPIC, task, msg)
    
    def _task_status_update(self):
        while True:
            task = ParserQueues.TASK_STATUS.get()
            TDDCLogging.debug('[{}:{}:{}]'.format(task.platform,
                                                  task.url,
                                                  task.status))
            self._successed_num += 1
            self._successed_pre_min += 1


def main():
    import gevent.monkey
    gevent.monkey.patch_all()
    
    def test(manager, a, b):
        cnt  = 0
        while cnt < 10:
            print('put: ', '{"test\":"'+'item, block, timeout'*30+"\"}")
            ParserQueues.CRAWL.put(json.loads('{"test\":"'+'item, block, timeout'*30+"\"}"))
            cnt += 1

    ParseTaskManager(test)
    
    while True:
        gevent.sleep(60)

if __name__ == '__main__':
    main()