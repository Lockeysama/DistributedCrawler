# -*- coding: utf-8 -*-
'''
Created on 2017年4月14日

@author: chenyitao
'''

from common.simple_tools import get_mac_address

# Crawler ID
CRAWLER_ID = 1

# Crawl Event Topic Info
CRAWL_EVENT_TOPIC_NAME = 'tddc_c_event'
CRAWL_EVENT_TOPIC_GROUP = 'tddc.c.{mac}.{id}'.format(mac=get_mac_address(),
                                                     id=CRAWLER_ID)

# Crawl Topic Info
CRAWL_TOPIC_GROUP = 'tddc.c.crawler'

# Crawler Concurrent
CRAWLER_CONCURRENT = 16

# DB Push Concurrent
DB_PUSH_CONCURRENT = 8

# Storage Family
STORAGE_FAMILY = ''

# Crawl Queue Switch
CRAWL_QUEUE_SWITCH = 32
