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

    # Task Input Queue
    TASK_INPUT = Queue()

    # Task Output Queue
    TASK_OUTPUT = Queue()

    # New Exception Queue
    NEW_EXCEPTION = Queue()

    # Exception Task Queue
    EXCEPTION_TASK = Queue()

    # Waiting For Storage Queue
    STORAGE = Queue()

    # Task Record Queue
    TASK_RECORD = Queue()

    # Task Status Queue
    TASK_STATUS = Queue()

    # Rules Moulds Update Queue
    RULES_MOULDS_UPDATE = Queue()
