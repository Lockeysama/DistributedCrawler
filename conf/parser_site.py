# -*- coding: utf-8 -*-
'''
Created on 2017年4月12日

@author: chenyitao
'''
from common.simple_tools import get_mac_address

# Parser ID
PARSER_ID = 1

# Parse Rules HBase Table Info
PARSE_RULES_HBASE_TABLE = 'tddc_p_rules'
PARSE_RULES_HBASE_FAMILY = 'rules'
PARSE_RULES_HBASE_INDEX_QUALIFIER = 'index'

# Parse Event Topic Info
PARSE_EVENT_TOPIC_NAME = 'tddc_p_event'
PARSE_EVENT_TOPIC_GROUP = 'tddc.p.{mac}.{id}'.format(mac=get_mac_address(), id=PARSER_ID)

# Parse Task Topic Info
PARSE_TOPIC_GROUP = 'tddc.p.parser'

# Parser Concurrent
PARSER_CONCURRENT = 8

# DB Fetch Concurrent
DB_FETCH_CONCURRENT = 8

# DB Push Concurrent
DB_PUSH_CONCURRENT = 2

