# -*- coding: utf-8 -*-
'''
Created on 2017年4月12日

@author: chenyitao
'''

import random
from enum import Enum


WorkerModel = Enum('WorkerModel', ('Crawler', 'Parser', 'ProxyChecker', 'Monitor'))

# Test
TEST = True

#Client ID
CLIENT_ID = 1

PLATFORM_SUFFIX = '_test' if TEST else ''

# Client Status
STATUS = True

# Worker Model
MODEL = WorkerModel.Crawler
# MODEL = WorkerModel.Parser
# MODEL = WorkerModel.PROXY_CHECKER
# MODEL = WorkerModel.Monitor

# ZK info
ZK_HOST_PORTS = ['72.127.2.48:2181']

# Kafka Info
KAFKA_HOST_PORT = '72.127.2.48:9092'

# HBase Info
HBASE_HOST_PORTS = ['72.127.2.48:9090']
HBASE_HOST_PORT = random.choice(HBASE_HOST_PORTS)

# Task Base Info Table Info
TASK_BASE_INFO_HBASE_TABLE = 'tddc_task_base'
TASK_BASE_INFO_HBASE_FAMILY = 'info'
TASK_BASE_INFO_HBASE_INDEX_QUALIFIER = 'index'

# Redis Info
REDIS_NODES = [{'host': '72.127.2.48', 'port': '7000'},
               {'host': '72.127.2.48', 'port': '7001'},
               {'host': '72.127.2.48', 'port': '7002'},
               {'host': '72.127.2.48', 'port': '7003'},
               {'host': '72.127.2.48', 'port': '7004'},
               {'host': '72.127.2.48', 'port': '7005'}]

# Parse Task Topic Info
PARSE_TOPIC_NAME = 'tddc_parse'

# Crawl Task Topic Info
CRAWL_TOPIC_NAME = 'tddc_crawl'

# Exception Task Topic Info
EXCEPTION_TOPIC_NAME = 'tddc_exception'

# Task Status HSet Prefix
TASK_STATUS_HSET_PREFIX = 'tddc.task.status'

# Cookies HSet
COOKIES_HSET = 'tddc.cookies'
