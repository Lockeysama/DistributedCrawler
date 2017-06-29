# -*- coding: utf-8 -*-
'''
Created on 2017年6月20日

@author: chenyitao
'''

from common.log.logger import TDDCLogging

from ..parse_rule_base import ParseRuleBase


class WeidaiBidDetailExtra(ParseRuleBase):
    '''
    classdocs
    '''

    platform = 'weidai'

    feature = 'weidai.bid_detail_extra'

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
        self._get_detail_extra_info(data)

    def _get_detail_extra_info(self, data):
        borrower = data.get('borrower')
        self.items['realName'] = borrower.get('realName')
        self.items['age'] = borrower.get('age')
        self.items['sex'] = borrower.get('sex') 
        self.items['married'] = borrower.get('married')
        self.items['nativePlace'] = borrower.get('nativePlace')
        self.items['nativeSubPlace'] = borrower.get('nativeSubPlace')
        endorsed = data.get('endorsed')
        self.items['models'] = endorsed.get('models')  # 型号
        self.items['licence'] = endorsed.get('licence')  # 车牌号
        self.items['miles'] = endorsed.get('miles')  # 行驶公里数
        self.items['originalPrice'] = endorsed.get('originalPrice')
        borrower_summary = data.get('borrowerSummary')
        self.items['repayedOffPeriods'] = borrower_summary.get('repayedOffPeriods')  # 历史还清期数
        self.items['repayPeriods'] = borrower_summary.get('repayPeriods')  # 待还款
        self.items['overduePeriods'] = borrower_summary.get('overduePeriods')  # 历史逾期次数
