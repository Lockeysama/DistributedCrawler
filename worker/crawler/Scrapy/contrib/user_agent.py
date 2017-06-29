#!/usr/bin/python
#-*-coding:utf-8-*-

'''
Created on 2015年8月7日

@author: chenyitao1
'''

import random
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
from worker.crawler.crawler import settings


class CustomUserAgent(UserAgentMiddleware):
    '''
    user agent
    '''
    
    user_agent_list = settings.attributes['USER_AGENT'].value

    def _user_agent(self, spider):
        '''
        user agent
        '''
        if hasattr(spider, 'user_agent'):
            return spider.user_agent
        return random.choice(self.user_agent_list)

    def process_request(self, request, spider):
        user_agent = self._user_agent(spider)
        if user_agent:
            request.headers['User-Agent'] = user_agent
