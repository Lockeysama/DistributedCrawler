# -*- coding: utf-8 -*-
'''
Created on 2017年4月18日

@author: chenyitao
'''

from worker.parser.models.parse_rule_base import ParseRuleBase


class CheokWantBuyDetail(ParseRuleBase):
    '''
    classdocs
    '''
    
    platform = 'cheok'
    
    feature = 'cheok.want_buy_detail'

    def _parse(self):
        if self._body_type == self.HTML:
            self._want_buy_detail()
    
    def _want_buy_detail(self):
        tmp = self._xpath('//*[@class="show-car-det"]//*[@class="title"]/span/text()')
        title = tmp[0].encode('utf-8')
        self.items['title'] = title


def main():
    from common.models import Task
    task = Task()
    with open('cheok_detail.html', 'r') as f:
        task.__dict__ = {'body': f.read()}
    CheokWantBuyDetail(task)
    
if __name__ == '__main__':
    main()
