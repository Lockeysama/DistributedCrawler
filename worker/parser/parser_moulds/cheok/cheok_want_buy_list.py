# -*- coding: utf-8 -*-
'''
Created on 2017年4月18日

@author: chenyitao
'''

from worker.parser.parser_moulds.parse_rule_base import ParseRuleBase
from common.models import Task

class CheokWantBuyList(ParseRuleBase):
    '''
    classdocs
    '''

    platform = 'cheok'

    feature = 'cheok.want_buy_list'
    
    version = '1495799999'

    def _parse(self):
        if self._body_type != self.JSON:
            print('(%s)Error. Not JSON.' % self.__class__)
            return
        self._want_buy_list()

    def _want_buy_list(self):
        if self._json_dict.get('code') != 1:
            print('(%s)Error. Response Code:%d.' % (self.__class__, self._json_dict.get('code', -1000)))
            return
        objs = self._json_dict.get('object')
        if objs and len(objs):
            base_url = 'http://www.cheok.com/{cityAcronym}/sn/{carSourceNo}.html'
            for info in objs:
                url = base_url.format(cityAcronym=info.get('cityAcronym'),
                                      carSourceNo=info.get('carSourceNo'))
                task = Task()
                task.url = url
                task.platform = self.platform
                task.feature = 'cheok.want_buy_detail'
                task.cookie = 'JSESSIONID=3A32AF91FE59B1F06A61954C280DFC12'
                task.headers = {'Referer': ('http://www.cheok.com/car/cp_' 
                                            + str(self._json_dict.get('page').get('currentPage')))}
                self._md5_mk.update(url)
                task.row_key = self._md5_mk.hexdigest()
                self.tasks.append(task)
      
        
def main():
    task = Task()
    with open('cheok_list.html', 'r') as f:
        task.__dict__ = {'body': f.read()}
    CheokWantBuyList(task)

if __name__ == '__main__':
    main()