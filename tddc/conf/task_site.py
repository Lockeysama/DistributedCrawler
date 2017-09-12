# -*- coding: utf-8 -*-
'''
Created on 2017年5月23日

@author: chenyitao
'''

class TaskSite(object):
    '''
    classdocs
    '''
    STATUS_LOGGER_ENABLE = True

    BASE_INFO_TABLE = 'tddc_task_base'
    BASE_INFO_FAMILY = 'info'
    BASE_INFO_QUALIFIER = 'index'

    # Task Input Topic Info
    TASK_INPUT_TOPIC = ''
    TASK_INPUT_TOPIC_GROUP = ''

    # Task Output Topic Info
    TASK_OUTPUT_TOPIC = ''
    TASK_OUTPUT_TOPIC_GROUP = ''

    # Task Status HSet Prefix
    STATUS_HSET_PREFIX = 'tddc.task.status'

    # Task Record HSet Prefix
    RECORD_HSET_PREFIX = 'tddc.task.record'

    # Local Task Queue Size
    LOCAL_TASK_QUEUE_SIZE = 200