# -*- coding: utf-8 -*-
'''
Created on 2017年4月12日

@author: chenyitao
'''

import gevent.queue

from .define import WorkerModel
from conf.base_site import MODEL

# Event Queue
EVENT_QUEUE = gevent.queue.Queue()

# Exception Queue
EXCEPTION_QUEUE = gevent.queue.Queue()

# Waiting For Crawl Queue
CRAWL_QUEUE = gevent.queue.Queue()

# Crawled Queue
PARSE_QUEUE = gevent.queue.Queue()

# Waiting For Storage Queue
STORAGE_QUEUE = gevent.queue.Queue()

if MODEL == WorkerModel.CRAWLER:
    # Task Base Info Update Queue
    TASK_BASE_INFO_UPDATE_QUEUE = gevent.queue.Queue()
    # Proxy IP Platform Queue 
    PROXY_IP_PLATFORM_QUEUE = gevent.queue.Queue()
    # Platform Proxy Queues
    PLATFORM_PROXY_QUEUES = dict()
    # Unuseful Proxy Feedback Queue
    UNUSEFUL_PROXY_FEEDBACK_QUEUE = gevent.queue.Queue()
elif MODEL == WorkerModel.PARSER:
    # Parser Rules Moulds Update Queue
    PARSER_RULES_MOULDS_UPDATE_QUEUE = gevent.queue.Queue()
    # Waiting For Parse Queue
    WAITING_PARSE_QUEUE = gevent.queue.Queue()
elif MODEL == WorkerModel.PROXY_CHECKER:
    # Useful Proxy Queue
    USEFUL_PROXY_QUEUE = gevent.queue.Queue()
    # Source Proxy Queue
    HTTP_SOURCE_PROXY_QUEUE = gevent.queue.Queue()
    HTTPS_SOURCE_PROXY_QUEUE = gevent.queue.Queue()


def main():
    pass

if __name__ == '__main__':
    main()