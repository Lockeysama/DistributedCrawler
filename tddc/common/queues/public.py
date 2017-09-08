# -*- coding: utf-8 -*-
'''
Created on 2017年5月22日

@author: chenyitao
'''

from gevent.queue import Queue


class PublicQueues(object):
    # Event Queue
    EVENT = Queue()
    
    # Exception Queue
    EXCEPTION = Queue()
    
    # Waiting For Crawl Queue
    CRAWL = Queue()
    
    # Crawled Queue
    PARSE = Queue()
    
    # New Exception Queue
    NEW_EXCEPTION = Queue()
    
    # Exception Task Queue
    EXCEPTION_TASK = Queue()
    
    # Waiting For Storage Queue
    STORAGE = Queue()
    
    # Task Status Queue
    TASK_STATUS = Queue()
    
    # Task Status Remove Queue
    TASK_STATUS_REMOVE = Queue()
    
    # Rules Moulds Update Queue
    RULES_MOULDS_UPDATE = Queue()
