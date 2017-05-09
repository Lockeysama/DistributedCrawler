# -*- coding: utf-8 -*-
'''
Created on 2017年4月14日

@author: chenyitao
'''

import json
import gevent

from common.models.task import Task
from base.task.task_manager_base import TaskManagerBase
from common.queues import PARSE_QUEUE, CRAWL_QUEUE, TASK_STATUS_QUEUE, TASK_STATUS_REMOVE_QUEUE
from conf.base_site import STATUS, PARSE_TOPIC_NAME, CRAWL_TOPIC_NAME
from conf.crawler_site import CRAWLER_CONCURRENT, CRAWL_TOPIC_GROUP
from plugins.mq.kafka_manager.kafka_helper import KafkaHelper


class CrawlTaskManager(TaskManagerBase):
    '''
    classdocs
    '''
    
    topics = {}

    def __init__(self):
        '''
        Constructor
        '''
        print('-->Task Manager Is Starting.')
        super(CrawlTaskManager, self).__init__()
        self._start_mq_server()
        print('-->Task Manager Was Ready.')

    def _start_mq_server(self):
        gevent.spawn(self._push_parse_task)
        gevent.sleep()
        self._crawl_task_consumer = KafkaHelper.make_consumer(CRAWL_TOPIC_NAME,
                                                              CRAWL_TOPIC_GROUP)
        gevent.spawn(self._fetch_crawl_task)
        gevent.sleep()

    def _fetch_crawl_task(self):
        print('--->Crawl Task Consumer Was Ready.')
        pause = False
        while STATUS:
            if CRAWL_QUEUE.qsize() > CRAWLER_CONCURRENT / 4:
                if not pause:
                    self._crawl_task_consumer.commit()
                    self._crawl_task_consumer.unsubscribe()
                    pause = True
                    print('Crawl Task Consumer Was Paused.')
                gevent.sleep(1)
                continue
            if pause:
                self._crawl_task_consumer.subscribe(CRAWL_TOPIC_NAME)
                pause = False
                print('Crawl Task Consumer Was Resumed.')
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
                CRAWL_QUEUE.put(task)
                TASK_STATUS_QUEUE.put(task)
            else:
                self._consume_msg_exp('CRAWL_TASK_ERR', item)
    
    def _push_parse_task(self):
        print('--->Parse Task Producer Was Ready.')
        while STATUS:
            task = PARSE_QUEUE.get()
            if not isinstance(task, Task):
                print('_push_parse_task', task)
                continue
            if not self._push_task(PARSE_TOPIC_NAME, task):
                print('_push_parse_task', task)
            else:
                TASK_STATUS_REMOVE_QUEUE.put(task)


def main():
    import gevent.monkey
    gevent.monkey.patch_all()
    
    CrawlTaskManager()
    while STATUS:
        gevent.sleep(1)

if __name__ == '__main__':
    main()
