# -*- coding: utf-8 -*-
'''
Created on 2017年4月12日

@author: chenyitao
'''

from gevent.queue import Queue
import multiprocessing
import gevent

# Event Queue
EVENT_QUEUE = Queue()

# Exception Queue
EXCEPTION_QUEUE = Queue()

# Waiting For Crawl Queue
CRAWL_QUEUE = gevent.queue.JoinableQueue()

# Crawled Queue
PARSE_QUEUE = Queue()

# Waiting For Storage Queue
STORAGE_QUEUE = gevent.queue.JoinableQueue()

# Task Status Queue
TASK_STATUS_QUEUE = Queue()

# Task Status Remove Queue
TASK_STATUS_REMOVE_QUEUE = Queue()

# Rules Moulds Update Queue
RULES_MOULDS_UPDATE_QUEUE = Queue()

## Crawler
# Task Base Info Update Queue
TASK_BASE_INFO_UPDATE_QUEUE = Queue()
# Proxy IP Platform Queue 
PROXY_IP_PLATFORM_QUEUE = Queue()
# Platform Proxy Queues
PLATFORM_PROXY_QUEUES = dict()
# Unuseful Proxy Feedback Queue
UNUSEFUL_PROXY_FEEDBACK_QUEUE = Queue()

## Parser
# Parser Rules Moulds Update Queue
PARSER_RULES_MOULDS_UPDATE_QUEUE = Queue()
# Waiting For Parse Queue
WAITING_PARSE_QUEUE = Queue()

## Proxy Checker
# Useful Proxy Queue
USEFUL_PROXY_QUEUE = Queue()
# Source Proxy Queue
HTTP_SOURCE_PROXY_QUEUE = Queue()
HTTPS_SOURCE_PROXY_QUEUE = Queue()
