# -*- coding: utf-8 -*-
'''
Created on 2017年5月19日

@author: chenyitao
'''


import random

from conf.base_site import REDIS_NODES, COOKIES_HSET
from worker.crawler.event import EventManagre, TDDCEvent
from common.queues import CrawlerQueues

from plugins import RedisClient


class CookiesManager(RedisClient):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        super(CookiesManager, self).__init__(REDIS_NODES)
        EventManagre().register(TDDCEvent.COOKIE_UPDATE, self._update_cookie)

    def _update_cookie(self, event):
        info = event.detail
        platform = info.get('platform')
        if not platform:
            return
        cookies = self.hget(COOKIES_HSET, platform)
        CrawlerQueues.PLATFORM_COOKIES[platform] = cookies

    @staticmethod
    def get_cookie(platform):
        cookies = CrawlerQueues.PLATFORM_COOKIES.get(platform)
        return random.choice(cookies) if cookies else None 

        
def main():
    pass

if __name__ == '__main__':
    main()
