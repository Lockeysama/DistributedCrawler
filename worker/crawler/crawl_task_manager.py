# -*- coding: utf-8 -*-
'''
Created on 2017年4月14日

@author: chenyitao
'''

import json
import gevent

from base.task.task_manager_base import TaskManagerBase
from common.queues import PARSE_QUEUE, CRAWL_QUEUE, EVENT_QUEUE
from conf.base_site import STATUS, PARSE_TOPIC_NAME, CRAWL_TOPIC_NAME
from worker.parser.models.event import Event
from conf.crawler_site import CRAWL_EVENT_TOPIC_NAME, CRAWL_EVENT_TOPIC_GROUP,\
    CRAWL_TOPIC_GROUP
from worker.crawler.models.crawl_task import CrawlTask

SIGNAL_TASK_MANAGER_READY = object()


class CrawlTaskManager(TaskManagerBase):
    '''
    classdocs
    '''

    def __init__(self, callback=None):
        '''
        Constructor
        '''
        print('-->Task Manager Is Starting.')
        super(CrawlTaskManager, self).__init__()
        self._callback = callback
        self._event_consumer = None
        self._event_consumer_tag = 1
        self._parse_task_producer = None
        self._parse_task_producer_tag = 2
        self._crawl_task_consumer = None
        self._crawl_task_consumer_tag = 3
        self._tag_num = 1 + 2 + 3
        self._cur_tag_num = 0
        self._start_mq_server()

    def _start_mq_server(self):
        self._parse_task_producer = self.make_producer(PARSE_TOPIC_NAME)
        gevent.spawn(self._push_parse_task)
        gevent.sleep()
        self._event_consumer = self.make_consumer(CRAWL_EVENT_TOPIC_NAME,
                                                  CRAWL_EVENT_TOPIC_GROUP,
                                                  True)
        gevent.spawn(self._fetch_event)
        gevent.sleep()
        self._crawl_task_consumer = self.make_consumer(CRAWL_TOPIC_NAME,
                                                       CRAWL_TOPIC_GROUP,
                                                       True)
        gevent.spawn(self._fetch_crawl_task)
        gevent.sleep()

    def _ready(self, tag):
        self._cur_tag_num += tag
        if self._cur_tag_num == self._tag_num:
            print('-->Task Manager Was Ready.')
            if not self._callback:
                return
            self._callback(self)

    def _consume_msg_exp(self, exp_type, info, exception=None):
        if 'JSON_ERR' in exp_type:
            print('*'*5+exp_type+'*'*5+
                  '\nException: '+info+'\n'+
                  exception.message+'\n'+
                  '*'*(10+len(exp_type))+'\n')
        elif 'TASK_ERR' in exp_type or 'EVENT_ERR' in exp_type:
            print('*'*5+exp_type+'*'*5+
                  '\nException: '+
                  'item={item}\n'.format(item=info)+
                  'item_type={item_type}\n'.format(item_type=type(info))+
                  '*'*(10+len(exp_type))+'\n')

    def _fetch_crawl_task(self):
        print('--->Crawl Task Consumer Was Ready.')
        self._ready(self._crawl_task_consumer_tag)
        while STATUS:
            msgs = self._crawl_task_consumer.start()
            for msg in msgs:
                try:
                    item = json.loads(msg.value)
                except Exception, e:
                    self._consume_msg_exp('CRAWL_TASK_JSON_ERR', msg.value, e)
                else:
                    if item and isinstance(item, dict) and item.get('url', None):
                        task = CrawlTask(item)
                        CRAWL_QUEUE.put(task)
                    else:
                        self._consume_msg_exp('CRAWL_TASK_ERR', item) 
                        continue
            if CRAWL_QUEUE.qsize() > 64:
                self._crawl_task_consumer.pause()
            elif CRAWL_QUEUE.qsize() < 32:
                self._crawl_task_consumer.resume()

    def _fetch_event(self):
        print('--->Crawl Event Consumer Was Ready.')
        self._ready(self._event_consumer_tag)
        while STATUS:
            msgs = self._event_consumer.start()
            for msg in msgs:
                try:
                    item = json.loads(msg.value)
                except Exception, e:
                    self._consume_msg_exp('EVENT_JSON_ERR', msg.value, e)
                else:
                    if item and isinstance(item, dict) and item.get('type', None):
                        event = Event(item)
                        EVENT_QUEUE.put(event)
                    else:
                        self._consume_msg_exp('EVENT_ERR', item) 

    def _push_parse_task(self):
        print('--->Parse Task Producer Was Ready.')
        self._ready(self._parse_task_producer_tag)
        while STATUS:
            task = PARSE_QUEUE.get()
            msg = json.dumps(task.__dict__)
            if msg:
                self._parse_task_producer.push(msg)
    
    def __del__(self):
        print('del', self.__class__)
        

def main():
    import gevent.monkey
    gevent.monkey.patch_all()
    
    CrawlTaskManager()
    while STATUS:
        gevent.sleep(1)

if __name__ == '__main__':
    main()
