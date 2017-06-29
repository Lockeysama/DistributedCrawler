# -*- coding: utf-8 -*-
'''
Created on 2017年6月20日

@author: chenyitao
'''

from common.log.logger import TDDCLogging
from common.models import Task

from ..parse_rule_base import ParseRuleBase


class WeidaiShowBidList(ParseRuleBase):
    '''
    classdocs
    '''
    
    platform = 'weidai'

    feature = 'weidai.show_bid_list'
    
    version = '1495799999'

    def _parse(self):
        if not self._json_dict.get('success'):
            TDDCLogging.warning('Crawled[{}:{}] Failed.'.format(self._task.platform,
                                                                self._task.url))
            return
        data = self._json_dict.get('data')
        if not data:
            TDDCLogging.warning('Crawled[{}:{}] Exception.'.format(self._task.platform,
                                                                   self._task.url))
            return
        if data.get('pageIndex') == 1:
            self._make_bid_list_tasks(data)
        self._make_detail_task(data.get('data'))

    def _make_bid_list_tasks(self, data):
        total_page_number = data.get('count')
        if not total_page_number:
            return
        base_url = ('https://www.weidai.com.cn/list/bidList'
                    '?type=0&periodType=0&sort=0&page={page_index}&rows=10')
        tmp = []
        for page_index in range(2, total_page_number/10+2):
            url = base_url.format(page_index=page_index)
            task = Task()
            task.url = url
            task.platform = self.platform
            task.feature = self.feature
            task.headers = {'Referer': 'https://www.weidai.com.cn/list/showBidList',
                            'X-Requested-With': 'XMLHttpRequest'}
            self._md5_mk.update(url)
            task.row_key = self._md5_mk.hexdigest()
            tmp.append(task)
            if page_index % 100 == 0 or page_index == total_page_number:
                self.tasks.extend(tmp)
                tmp = []

    def _make_detail_task(self, data):
        referer_base_url = 'https://www.weidai.com.cn/bid/showBidDetail?hash={hash}' 
        base_url = 'https://www.weidai.com.cn/bid/bidDetail?hash={hash}&bid='
        for detail_info in data:
            path = detail_info.get('hash')
            if not path:
                TDDCLogging.warning('Path Is None.')
                return
            task = Task()
            task.url = base_url.format(hash=path)
            task.platform = self.platform
            task.feature = 'weidai.bid_detail'
            task.headers = {'Referer': referer_base_url.format(hash=path),
                            'X-Requested-With': 'XMLHttpRequest'}
            self._md5_mk.update(task.url)
            task.row_key = self._md5_mk.hexdigest()
            self.tasks.append(task)
