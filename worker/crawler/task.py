# -*- coding: utf-8 -*-
'''
Created on 2017年4月14日

@author: chenyitao
'''

import json
import gevent

from base.models.task import Task
from base.task.task_manager_base import TaskManagerBase
from common.queues import PARSE_QUEUE, CRAWL_QUEUE
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
        while STATUS:
            if not CRAWL_QUEUE.qsize() < CRAWLER_CONCURRENT / 2:
                gevent.sleep(1)
            for record in self._crawl_task_consumer:
                try:
                    item = json.loads(record.value)
                except Exception, e:
                    self._consume_msg_exp('CRAWL_TASK_JSON_ERR', record.value, e)
                else:
                    if item and isinstance(item, dict) and item.get('url', None):
                        task = Task(**item)
                        CRAWL_QUEUE.put(task)
                        if CRAWL_QUEUE.qsize() >= CRAWLER_CONCURRENT:
                            break
                    else:
                        self._consume_msg_exp('CRAWL_TASK_ERR', item) 
            
    def _push_parse_task(self):
        print('--->Parse Task Producer Was Ready.')
        while STATUS:
            task = PARSE_QUEUE.get()
            try:
                msg = json.dumps(task.__dict__)
                if msg:
                    self._producer.send(PARSE_TOPIC_NAME, msg)
            except Exception, e:
                print(e)


def main():
    import gevent.monkey
    gevent.monkey.patch_all()
    
    CrawlTaskManager()
    while STATUS:
        gevent.sleep(1)

if __name__ == '__main__':
    main()
