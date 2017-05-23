# -*- coding: utf-8 -*-
'''
Created on 2017年5月23日

@author: chenyitao
'''

class TaskSite(object):
    '''
    classdocs
    '''

    BASE_INFO_TABLE = 'tddc_task_base'
    BASE_INFO_FAMILY = 'info'
    BASE_INFO_QUALIFIER = 'index'

    # Parse Task Topic Info
    PARSE_TOPIC = 'tddc_parse'
    
    # Crawl Task Topic Info
    CRAWL_TOPIC = 'tddc_crawl'
    
    # Task Status HSet Prefix
    STATUS_HSET_PREFIX = 'tddc.task.status'
