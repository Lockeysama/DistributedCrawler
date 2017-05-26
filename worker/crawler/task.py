# -*- coding: utf-8 -*-
'''
Created on 2017年4月14日

@author: chenyitao
'''

import json
import gevent

from conf import CrawlerSite
from common.models import Task
from common.queues import CrawlerQueues
from log import TDDCLogging

from . import TaskManagerBase
from plugins import KafkaHelper


class CrawlTaskManager(TaskManagerBase):
    '''
    classdocs
    '''
    
    topics = {}

    def __init__(self):
        '''
        Constructor
        '''
        TDDCLogging.info('-->Task Manager Is Starting.')
        super(CrawlTaskManager, self).__init__()
        self._start_mq_server()
        TDDCLogging.info('-->Task Manager Was Ready.')

    def _start_mq_server(self):
        gevent.spawn(self._push_parse_task)
        gevent.sleep()
        self._crawl_task_consumer = KafkaHelper.make_consumer(CrawlerSite.KAFKA_NODES,
                                                              CrawlerSite.CRAWL_TOPIC,
                                                              CrawlerSite.CRAWL_TOPIC_GROUP)
        gevent.spawn(self._fetch_crawl_task)
        gevent.sleep()

    def _fetch_crawl_task(self):
        TDDCLogging.info('--->Crawl Task Consumer Was Ready.')
        pause = False
        while True:
            if CrawlerQueues.CRAWL.qsize() > CrawlerSite.CONCURRENT * 4:
                if not pause:
                    self._crawl_task_consumer.commit()
                    self._crawl_task_consumer.unsubscribe()
                    pause = True
                    TDDCLogging.info('Crawl Task Consumer Was Paused.')
                gevent.sleep(1)
                continue
            if pause and CrawlerQueues.CRAWL.qsize() < CrawlerSite.CONCURRENT / 2:
                self._crawl_task_consumer.subscribe(CrawlerSite.CRAWL_TOPIC)
                pause = False
                TDDCLogging.info('Crawl Task Consumer Was Resumed.')
            partition_records = self._crawl_task_consumer.poll(2000, 16)
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
            self._consume_msg_exp('CRAWL_TASK_JSON_ERR', record.value, e)
        else:
            if item and isinstance(item, dict) and item.get('url', None):
                task = Task(**item)
                task.status = Task.Status.WAIT_CRAWL
                CrawlerQueues.CRAWL.put(task)
                CrawlerQueues.TASK_STATUS.put(task)
            else:
                self._consume_msg_exp('CRAWL_TASK_ERR', item)
    
    def _push_parse_task(self):
        TDDCLogging.info('--->Parse Task Producer Was Ready.')
        while True:
            task, status = CrawlerQueues.PARSE.get()
            tmp = Task(**task.__dict__)
            task.status = Task.Status.CRAWL_SUCCESS
            if not isinstance(task, Task):
                TDDCLogging.error('')
                continue
            if not self._push_task(CrawlerSite.PARSE_TOPIC, tmp):
                TDDCLogging.error('')
            else:
                CrawlerQueues.TASK_STATUS_REMOVE.put(tmp)
                TDDCLogging.debug('[%s:%s] Crawled Successed(%d).' % (task.platform,
                                                                      task.row_key,
                                                                      status))
                self._successed_num += 1
                self._successed_pre_min += 1


def main():
    import gevent.monkey
    gevent.monkey.patch_all()
    
    CrawlTaskManager()
    while True:
        gevent.sleep(1)

if __name__ == '__main__':
    main()
