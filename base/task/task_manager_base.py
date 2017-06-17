# -*- coding: utf-8 -*-
'''
Created on 2017年4月7日

@author: chenyitao
'''

import json
import gevent

from common import TDDCLogging

from .task_status_updater import TaskStatusUpdater
from ..plugins import KafkaHelper
from conf.default import KafkaSite


class TaskManagerBase(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self._producer = KafkaHelper.make_producer(KafkaSite.KAFKA_NODES)
        self._task_status_updater = TaskStatusUpdater()
        self._successed_num = 0
        self._successed_pre_min = 0
        gevent.spawn(self._status_printer)
        gevent.sleep()

    def _status_printer(self):
        while True:
            gevent.sleep(60)
            TDDCLogging.info('Successed Status: [All=%d] [Pre Minute:%d]' % (self._successed_num,
                                                                             self._successed_pre_min))
            self._successed_pre_min = 0

    def _push_task(self, topic, task, times=0):
        if not task:
            return False
        msg = json.dumps(task.__dict__)
        if msg:
            try:
                self._producer.send(topic, msg)
            except Exception, e:
                print('_push_task', e)
                gevent.sleep(1)
                if times == 10:
                    return False 
                times += 1
                return self._push_task(topic, task, times)
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

