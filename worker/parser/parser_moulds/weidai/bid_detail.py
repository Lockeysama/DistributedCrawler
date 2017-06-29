# -*- coding: utf-8 -*-
'''
Created on 2017年6月20日

@author: chenyitao
'''

from common.log.logger import TDDCLogging
from common.models import Task

from ..parse_rule_base import ParseRuleBase


class WeidaiBidDetail(ParseRuleBase):
    '''
    classdocs
    '''

    platform = 'weidai'

    feature = 'weidai.bid_detail'

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
        self._make_detail_extra_task(data)

    def _make_detail_extra_task(self, data):
        uid = data.get('uid')
        path = self._task.url.split('hash=')[1].split('&')[0]
        base_url = ('https://www.weidai.com.cn/bid/queryBiddingExtraDetails'
                    '?hash={hash}&borrowerUid={uid}')
        task = Task()
        task.url = base_url.format(hash=path, uid=uid)
        task.platform = self.platform
        task.feature = 'weidai.bid_detail_extra'
        task.headers = self._task.headers
        self._md5_mk.update(task.url)
        task.row_key = self._md5_mk.hexdigest()
        self.tasks.append(task)
