# -*- coding: utf-8 -*-
'''
Created on 2017年4月12日

@author: chenyitao
'''

import json
import gevent

from conf.base_site import STATUS, PARSE_TOPIC_NAME, CRAWL_TOPIC_NAME
from conf.parser_site import PARSE_TOPIC_GROUP, PARSE_EVENT_TOPIC_NAME,\
    PARSE_EVENT_TOPIC_GROUP
from common.queues import PARSE_QUEUE, CRAWL_QUEUE
from base.task.task_manager_base import TaskManagerBase
from worker.parser.models.parse_task import ParseTask

SIGNAL_TASK_MANAGER_READY = object()


class ParseTaskManager(TaskManagerBase):
    '''
    classdocs
    '''

    event_topic_name = PARSE_EVENT_TOPIC_NAME
    
    event_topic_group = PARSE_EVENT_TOPIC_GROUP

    def __init__(self, callback=None):
        '''
        Constructor
        '''
        print('-->Task Manager Is Starting.')
        super(ParseTaskManager, self).__init__()
        self._callback = callback
        self._parse_task_consumer = None
        self._parse_task_consumer_tag = 2
        self._crawl_task_producer = None
        self._crawl_task_producer_tag = 3
        self._tag_num = 2 + 3
        self._cur_tag_num = 0
        self._start_mq_server()

    def _start_mq_server(self):
        self._parse_task_consumer = self.make_consumer(PARSE_TOPIC_NAME,
                                                       PARSE_TOPIC_GROUP,
                                                       True)
        gevent.spawn(self._fetch_parse_task)
        gevent.sleep()
        self._crawl_task_producer = self.make_producer(CRAWL_TOPIC_NAME)
        gevent.spawn(self._push_crawl_task)
        gevent.sleep()

    def _ready(self, tag):
        self._cur_tag_num += tag
        if self._cur_tag_num == self._tag_num:
            print('-->Task Manager Was Ready.')
            if not self._callback:
                return
            self._callback(self, SIGNAL_TASK_MANAGER_READY, None)

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

    def _fetch_parse_task(self):
        print('--->Parsing Task Consumer Was Ready.')
        self._ready(self._parse_task_consumer_tag)
        while STATUS:
            gevent.sleep(2)
            msgs = self._parse_task_consumer.start()
            for msg in msgs:
                try:
                    item = json.loads(msg.value)
                except Exception, e:
                    self._consume_msg_exp('PARSE_TASK_JSON_ERR', msg.value, e)
                else:
                    if item and isinstance(item, dict) and item.get('url', None):
                        task = ParseTask(parse_info_dict=item)
                        PARSE_QUEUE.put(task)
                    else:
                        self._consume_msg_exp('PARSE_TASK_ERR', item) 
                        continue
            if PARSE_QUEUE.qsize() > 32:
                self._parse_task_consumer.pause()
            elif PARSE_QUEUE.qsize() < 16:
                self._parse_task_consumer.resume()

    def _push_crawl_task(self):
        print('--->Crawl Task Producer Was Ready.')
        self._ready(self._crawl_task_producer_tag)
        while STATUS:
            task = CRAWL_QUEUE.get()
            msg = json.dumps(task.__dict__)
            if msg:
                self._crawl_task_producer.push(msg)
    
    def __del__(self):
        print('del', self.__class__)
        

def main():
    import gevent.monkey
    gevent.monkey.patch_all()
    
    def test(manager, a, b):
        cnt  = 0
        while cnt < 10:
            print('put: ', '{"test\":"'+'item, block, timeout'*30+"\"}")
            CRAWL_QUEUE.put(json.loads('{"test\":"'+'item, block, timeout'*30+"\"}"))
            cnt += 1
            
    ParseTaskManager(test)
    
    while STATUS:
        gevent.sleep(60)

if __name__ == '__main__':
    main()