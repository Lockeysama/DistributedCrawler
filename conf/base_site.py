# -*- coding: utf-8 -*-
'''
Created on 2017年4月12日

@author: chenyitao
'''

from common.define import WorkerModel

# Test
TEST = True

PLATFORM_SUFFIX = '_test' if TEST else ''

# Client Status
STATUS = True

# Worker Model
MODEL=WorkerModel.CRAWLER
# MODEL=WorkerModel.PARSER
# MODEL=WorkerModel.PROXY_CHECKER

# ZK info
ZK_HOST_PORTS = ['72.127.2.48:2181']

# Kafka Info
KAFKA_HOST = '72.127.2.48'
KAFKA_PORT = 9092

# HBase Info
HBASE_HOST_PORTS = ['72.127.2.48:9090']

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


def main():
    pass

if __name__ == '__main__':
    main()