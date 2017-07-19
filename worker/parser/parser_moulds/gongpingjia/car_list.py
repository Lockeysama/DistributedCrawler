# -*- coding: utf-8 -*-
'''
Created on 2017年7月14日

@author: chenyitao
'''

from common.models import Task

from ..parse_rule_base import ParseRuleBase


class GongpingjiaCarList(ParseRuleBase):
    '''
    classdocs
    '''
    
    platform = 'gongpingjia'

    feature = 'gongpingjia.car_list'
    
    version = '1495799999'

    def _parse(self):
        current_page = self._xpath('//*[@class="car_link"]/label[1]/text()')[0]
        if current_page == '1':
            amount_pages = int(self._xpath('//*[@class="car_link"]/label[2]/text()')[0])
            base = 'http://hz.gongpingjia.com/buy/car/ordinary/pg{pg_number}params/'
            for pg_number in range(2, amount_pages):
                task = Task()
                task.url = base.format(pg_number=pg_number)
                task.platform = self.platform
                task.feature = self.feature
                task.headers = {'Referer': base.format(pg_number=pg_number-1)}
                self._md5_mk.update(task.url)
                task.row_key = self._md5_mk.hexdigest()
                self.tasks.append(task)
        car_list = self._xpath('//*[@class="rmd_list_carInfo"]/p/a/@href')
        detail_base = 'http://hz.gongpingjia.com/buy/car/get-similar-price-car/?car_id={car_id}'
        for detail in car_list:
            car_id = detail.split('=')[1]
            task = Task()
            task.url = detail_base.format(car_id=car_id)
            task.platform = self.platform
            task.feature = 'gongpingjia.car_detail'
            task.headers = {'Referer': self._task.url}
            self._md5_mk.update(task.url)
            task.row_key = self._md5_mk.hexdigest()
            self.tasks.append(task)