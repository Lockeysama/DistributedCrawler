# -*- coding: utf-8 -*-
'''
Created on 2017年7月14日

@author: chenyitao
'''

from common.models import Task

from ..parse_rule_base import ParseRuleBase


class EvalList(ParseRuleBase):
    '''
    classdocs
    '''
    
    platform = 'gongpingjia'

    feature = 'gongpingjia.eval_list'
    
    version = '1495799999'

    def _parse(self):
        with open('./fp.csv', 'r') as f:
            data = f.read()
        urls_infos = data.split('\n')
        try:
            urls = [info.split(',')[0] for info in urls_infos[1:] if info != '']
            for url in urls:
                task = Task()
                task.url = url
                task.platform = self.platform
                task.feature = 'gongpingjia.eval_detail'
                self._md5_mk.update(task.url)
                task.row_key = self._md5_mk.hexdigest()
                self.tasks.append(task)
        except :
            pass
        print len(self.tasks)