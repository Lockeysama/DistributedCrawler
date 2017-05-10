# -*- coding: utf-8 -*-
'''
Created on 2017年5月5日

@author: chenyitao
'''

from common import get_mac_address
from .base_site import WorkerModel, CLIENT_ID, MODEL

EVENT_TOPIC = ''
if MODEL == WorkerModel.Crawler:
    EVENT_TOPIC = 'tddc_crawler_event'
elif MODEL == WorkerModel.Parser:
    EVENT_TOPIC = 'tddc_parser_event'
elif MODEL == WorkerModel.ProxyChecker:
    EVENT_TOPIC = 'tddc_proxy_checker_event'

EVENT_TOPIC_GROUP = 'tddc_{mac_addr}_{id}'.format(mac_addr=get_mac_address(),
                                                  id=CLIENT_ID)

    