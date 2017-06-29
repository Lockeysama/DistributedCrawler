# -*- coding: utf-8 -*-
'''
Created on 2017年6月26日

@author: chenyitao
'''

from ..parse_rule_base import ParseRuleBase


class HuichedaiInvestDetail(ParseRuleBase):
    '''
    classdocs
    '''

    platform = 'huichedai'

    feature = 'huichedai.invest_detail'

    version = '1495799999'

    def _parse(self):
        if self._xpath('//*[@class="aboutbd"]'):
            return
        self.items['gender'] = self.get_userinfo(1)
        self.items['age'] = self.get_userinfo(2)
        self.items['education'] = self.get_userinfo(3)
        self.items['married'] = self.get_userinfo(4)
        self.items['native_place'] = self.get_userinfo(5)
        self.items['real_estate'] = self.get_userinfo(6)
        self.items['sue'] = self.get_userinfo(7)
        self.items['credit'] = self._xpath('//*[@class="userinfoUl"]/li[8]/em/text()')[0].encode('utf-8')
        self.items['driving_license'] = self.get_carinfo(info_type=1, index=1)
        self.items['license'] = self.get_carinfo(info_type=1, index=2)
        self.items['code'] = self.get_carinfo(info_type=1, index=3)
        self.items['number'] = self.get_carinfo(info_type=1, index=4)
        self.items['brand'] = self.get_carinfo(info_type=2, index=1)
        self.items['model'] = self.get_carinfo(info_type=2, index=2)
        self.items['purchasing_date'] = self.get_carinfo(info_type=2, index=3)
        self.items['price'] = self.get_carinfo(info_type=2, index=4)
        self.items['displacement'] = self.get_carinfo(info_type=2, index=5)
        self.items['license_date'] = self.get_carinfo(info_type=2, index=6)

    def get_userinfo(self, index):
        userinfo_ul = '//*[@class="userinfoUl"]/li[{index}]/text()'
        result = self._xpath(userinfo_ul.format(index=index))
        if not len(result):
            return
        return result[0].encode('utf-8')

    def get_carinfo(self, info_type, index):
        carinfo_ul = '//*[@class="infoUl"][{info_type}]/li[{index}]/text()'
        result = self._xpath(carinfo_ul.format(info_type=info_type, index=index))
        if not len(result):
            return
        return result[0].encode('utf-8')
