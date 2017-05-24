# -*- coding: utf-8 -*-
'''
Created on 2017年5月19日

@author: chenyitao
'''


import random

from conf import CrawlerSite
from common.queues import CrawlerQueues

from worker.crawler.event import CrawlerEventCenter
from plugins import RedisClient
from common.models.events.event_base import EventType


class CookiesManager(RedisClient):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        super(CookiesManager, self).__init__(CrawlerSite.REDIS_NODES)
        CrawlerEventCenter().register(EventType.Crawler.COOKIES, self._update_cookie)

    def _update_cookie(self, event):
        info = event.detail
        platform = info.get('platform')
        if not platform:
            return
        cookies = self.hget(CrawlerSite.COOKIES_HSET, platform)
        CrawlerQueues.PLATFORM_COOKIES[platform] = cookies

    @staticmethod
    def get_cookie(platform):
        cookies = CrawlerQueues.PLATFORM_COOKIES.get(platform)
        return random.choice(cookies) if cookies else None 

        
def main():
    pass

if __name__ == '__main__':
    main()
