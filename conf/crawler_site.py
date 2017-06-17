# -*- coding: utf-8 -*-
'''
Created on 2017年4月14日

@author: chenyitao
'''

from conf.base_site import BaseSite


class CrawlerSite(BaseSite):

    # Crawler Concurrent
    CONCURRENT = 100

    # Crawler Topic Group
    CRAWL_TOPIC_GROUP = 'tddc.crawler'
