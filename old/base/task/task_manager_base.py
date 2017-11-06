# -*- coding: utf-8 -*-
'''
Created on 2017年4月7日

@author: chenyitao
'''

import json

import gevent
from tddc.common import TDDCLogging

from old.common.models.task import Task
from .task_cache_manager import TaskCacheManager
from ..plugins import KafkaHelper


class TaskManagerBase(KafkaHelper):
    '''
    classdocs
    '''

    def __init__(self, site, queues):
        '''
        Constructor
        '''
        super(TaskManagerBase, self).__init__()
        self._site = site
        self._queues = queues
        if site.TASK_STATUS_UPDATER_ENABLE:
            self._task_status_updater = TaskCacheManager(self._site)
            gevent.spawn(self._update_task_status)
            gevent.sleep()
        if site.TASK_OUTPUT_TOPIC:
            self._task_output_producer = self.make_producer(self._site.KAFKA_NODES)
            gevent.spawn(self._push_task)
            gevent.sleep()
        if site.TASK_INPUT_TOPIC:
            self._task_input_consumer = self.make_consumer(self._site.KAFKA_NODES,
                                                           self._site.TASK_INPUT_TOPIC,
                                                           self._site.TASK_INPUT_TOPIC_GROUP)
            gevent.spawn(self._fetch_task)
            gevent.sleep()

    def _fetch_task(self):
        TDDCLogging.info('--->Task Input Consumer Was Ready.')
        pause = False
        while True:
            if self._queues.TASK_INPUT.qsize() > self._site.LOCAL_TASK_QUEUE_SIZE:
                if not pause:
                    self._task_input_consumer.commit()
                    self._task_input_consumer.unsubscribe()
                    pause = True
                    TDDCLogging.info('Task Input Consumer Was Paused.')
                gevent.sleep(1)
                continue
            if pause and self._queues.TASK_INPUT.qsize() < self._site.LOCAL_TASK_QUEUE_SIZE / 2:
                self._task_input_consumer.subscribe(self._site.TASK_INPUT_TOPIC)
                pause = False
                TDDCLogging.info('Task Input Consumer Was Resumed.')
            partition_records = self._task_input_consumer.poll(2000, 16)
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
            self._consume_msg_exp('TASK_JSON_ERR', record.value, e)
        else:
            if item and isinstance(item, dict) and item.get('url', None):
                task = Task(**item)
                self.task_status_process(task)
                self._queues.TASK_INPUT.put(task)
            else:
                self._consume_msg_exp('TASK_ERR', item)

    def task_status_process(self, task):
        '''
        如需更改任务状态等操作，可以重写此方法
        '''
        pass

    def _push_task(self):
        TDDCLogging.info('--->Task Output Producer Was Ready.')
        while True:
            task = self._queues.TASK_OUTPUT.get()
            if not self._push(self._site.TASK_OUTPUT_TOPIC, task):
                TDDCLogging.error('Push Task Failed.')
            else:
                self.pushed(task)

    def pushed(self, task):
        '''
        新任务推送成功回调
        '''
        pass

    def ready_to_push(self, task):
        '''
        新任务推送前回调
        继续推送：return True
        '''
        return True

    def _push(self, topic, task, times=0):
        if not task:
            return False
        msg = json.dumps(task.__dict__)
        if msg:
            try:
                if self.ready_to_push(task): 
                    self._task_output_producer.send(topic, msg)
            except Exception, e:
                TDDCLogging.warning('Push Task Field: ' + e.message)
                gevent.sleep(1)
                if times == 10:
                    return False 
                return self._push(topic, task, times + 1)
            else:
                return True
        return False

    def _consume_msg_exp(self, exp_type, info, exception=None):
        if 'JSON_ERR' in exp_type:
            TDDCLogging.error('*'*5+exp_type+'*'*5+
                              '\nException: '+info+'\n'+
                              exception.message+'\n'+
                              '*'*(10+len(exp_type))+'\n')
        elif 'TASK_ERR' in exp_type or 'EVENT_ERR' in exp_type:
            TDDCLogging.error('*'*5+exp_type+'*'*5+
                              '\nException: '+
                              'item={item}\n'.format(item=info)+
                              'item_type={item_type}\n'.format(item_type=type(info))+
                              '*'*(10+len(exp_type))+'\n')

    def _update_task_status(self):
        while True:
            task, new_status, old_status = self._queues.TASK_STATUS.get()
            self.update_status(task, new_status, old_status)
            self.task_status_changed(task, new_status)

    def task_status_changed(self, task, new_status):
        '''
        任务状态改变
        '''
        pass
    
    def update_status(self, task, new_status, old_status):
        self._task_status_updater.update_status(task, new_status, old_status)

    def create_record(self, task):
        self._task_status_updater.create_record(task)