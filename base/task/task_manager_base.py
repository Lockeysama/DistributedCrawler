# -*- coding: utf-8 -*-
'''
Created on 2017年4月7日

@author: chenyitao
'''

from plugins.mq.kafka_manager.kafka_helper import KafkaHelper

class TaskManagerBase(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        print('-->MQ Manager Is Starting.')
        self._producer = KafkaHelper.make_producer()

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

