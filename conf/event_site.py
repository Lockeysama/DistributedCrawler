# -*- coding: utf-8 -*-
'''
Created on 2017年5月5日

@author: chenyitao
'''

from common.define import WorkerModel
from common.simple_tools import get_mac_address
from conf.base_site import CLIENT_ID, MODEL

EVENT_TOPIC = ''
if MODEL == WorkerModel.CRAWLER:
    EVENT_TOPIC = 'tddc_crawler_event'
elif MODEL == WorkerModel.PARSER:
    EVENT_TOPIC = 'tddc_parser_event'
elif MODEL == WorkerModel.PROXY_CHECKER:
    EVENT_TOPIC = 'tddc_proxy_checker_event'

EVENT_TOPIC_GROUP = 'tddc_{mac_addr}_{id}'.format(mac_addr=get_mac_address(),
                                                  id=CLIENT_ID)

    