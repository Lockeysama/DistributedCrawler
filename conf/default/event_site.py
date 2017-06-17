# -*- coding: utf-8 -*-
'''
Created on 2017年5月23日

@author: chenyitao
'''


class EventSite(object):
    
    EVENT_TOPIC = ''
    
    EVENT_TOPIC_GROUP = ''

    
# EVENT_TOPIC = ''
# if MODEL == WorkerModel.Crawler:
#     EVENT_TOPIC = 'tddc_crawler_event'
# elif MODEL == WorkerModel.Parser:
#     EVENT_TOPIC = 'tddc_parser_event'
# elif MODEL == WorkerModel.ProxyChecker:
#     EVENT_TOPIC = 'tddc_proxy_checker_event'
# 
# EVENT_TOPIC_GROUP = 'tddc_{mac_addr}_{id}'.format(mac_addr=get_mac_address(),
#                                                   id=CLIENT_ID)