# -*- coding: utf-8 -*-
'''
Created on 2017年6月23日

@author: chenyitao
'''

from common.models import Task

from ..parse_rule_base import ParseRuleBase


class HuichedaiIvnestList(ParseRuleBase):
    '''
    classdocs
    '''
    
    platform = 'huichedai'

    feature = 'huichedai.invest_list'
    
    version = '1495799999'

    def _parse(self):
        cur_page = self._doc.xpath('//*[@class="pager-content"]/span/text()')[0]
        base = 'http://www.huichedai.com/invest/index{page_number}.html'
        if cur_page == '1':
            page_cnt = self._doc.xpath('//*[@class="pager-content"]/text()')[0]
            page_cnt = int(page_cnt.split('/')[1][:-2])
            tmp = []
            for index in range(2, page_cnt + 1):
                url = base.format(page_number=index)
                task = Task()
                task.url = url
                task.platform = self.platform
                task.feature = self.feature
                task.headers = {'Referer': base.format(page_number=index+1 if index == 2 else index-1)}
                self._md5_mk.update(url)
                task.row_key = self._md5_mk.hexdigest()
                tmp.append(task)
                if index % 100 == 0 or index == page_cnt:
                    self.tasks.extend(tmp)
                    tmp = []
        detail_base = 'http://www.huichedai.com{page}'
        detail_urls = self._doc.xpath('//*[@class="em strong"]/@href')
        for detail in detail_urls:
            url = detail_base.format(page=detail)
            task = Task()
            task.url = url
            task.platform = self.platform
            task.feature = 'huichedai.invest_detail'
            task.headers = {'Referer': base.format(page_number='' if cur_page == '1' else cur_page)}
            self._md5_mk.update(url)
            task.row_key = self._md5_mk.hexdigest()
            self.tasks.append(task)
