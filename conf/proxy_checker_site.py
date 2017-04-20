# -*- coding: utf-8 -*-
'''
Created on 2017年4月17日

@author: chenyitao
'''
from common.simple_tools import get_mac_address


# Proxy Checker ID
PROXY_CHECKER_ID = 1

# Is Proxy Source Process Start.
IS_PROXY_SOURCE_PROCESS_START = True

# Proxy Checker Rules HBase Table Info
PROXY_CHECKER_RULES_CONF_PATH = './conf/proxy_checker_rule_index/%s.json'
PROXY_CHECKER_RULES_HBASE_TABLE = 'tddc_pc_rules'
PROXY_CHECKER_RULES_HBASE_FAMILY = 'rules'
PROXY_CHECKER_RULES_HBASE_INDEX_QUALIFIER = 'index'

# Proxy Cehcker Event Topic Info
PROXY_CHECKER_EVENT_TOPIC_NAME = 'tddc_pc_event'
PROXY_CHECKER_EVENT_TOPIC_GROUP = 'tddc.pc.{mac}.{id}'.format(mac=get_mac_address(), id=PROXY_CHECKER_ID)

# Proxy Checker Task Topic Info
PROXY_CHECKER_TOPIC_GROUP = 'tddc.pc.parser'

# Proxy Checker Concurrent
PROXY_CHECKER_CONCURRENT = 16

# Source Proxy Set Key
HTTP_SOURCE_PROXY_SET_KEY = 'tddc:test:proxy:ip_src:http'
HTTPS_SOURCE_PROXY_SET_KEY = 'tddc:test:proxy:ip_src:https'

# Platform Proxy Set Base Key
PLATFORM_PROXY_SET_BASE_KEY = 'tddc:test:proxy:ip_dst:'

# Proxy Pubsub Pattern
PROXY_PUBSUB_PATTERN = 'tddc:test:proxy:pubsub:*'
