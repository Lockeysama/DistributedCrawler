# -*- coding: utf-8 -*-
'''
Created on 2017年4月12日

@author: chenyitao
'''

import json
import gevent

from conf.base_site import PARSE_TOPIC_NAME, CRAWL_TOPIC_NAME, KAFKA_HOST_PORT
from conf.parser_site import PARSE_TOPIC_GROUP, PARSER_CONCURRENT
from common.queues import PARSE_QUEUE, CRAWL_QUEUE, TASK_STATUS_QUEUE
from ..base import TaskManagerBase
from common import TDDCLogging
from plugins import KafkaHelper
from common.models import Task

SIGNAL_TASK_MANAGER_READY = object()


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
        self._start_mq_server()
        TDDCLogging.info('-->Task Manager Was Ready.')

    def _start_mq_server(self):
        self._consumer = KafkaHelper.make_consumer(KAFKA_HOST_PORT,
                                                   PARSE_TOPIC_NAME,
                                                   PARSE_TOPIC_GROUP)
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
            if PARSE_QUEUE.qsize() > PARSER_CONCURRENT * 4:
                if not pause:
                    self._consumer.commit()
                    self._consumer.unsubscribe()
                    pause = True
                    TDDCLogging.info('Parsing Task Consumer Was Paused.')
                gevent.sleep(1)
                continue
            if pause:
                self._consumer.subscribe(PARSE_TOPIC_NAME)
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
                PARSE_QUEUE.put(task)
                TASK_STATUS_QUEUE.put(task)
            else:
                self._consume_msg_exp('PARSE_TASK_ERR', item)

    def _push_new_crawl_task(self):
        TDDCLogging.info('--->Parser Task Producer Was Ready.')
        while True:
            task = CRAWL_QUEUE.get()
            msg = json.dumps(task.__dict__)
            if msg:
                self._push_task(CRAWL_TOPIC_NAME, task, msg)
    
    def _task_status_update(self):
        while True:
            task = TASK_STATUS_QUEUE.get()
            TDDCLogging.debug('[%s:%s] Parsed Successed.' % (task.platform,
                                                             task.url))
            self._successed_num += 1
            self._successed_pre_min += 1


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
    
    while True:
        gevent.sleep(60)

if __name__ == '__main__':
    main()