# -*- coding: utf-8 -*-
'''
Created on 2017年4月13日

@author: chenyitao
'''

import time

from worker.crawler.models.crawl_task import CrawlTask
from worker.parser.models.parse_rule_base import ParseRuleBase

class CheokHomepage(ParseRuleBase):
    '''
    classdocs
    '''
    
    platform = 'cheok'

    feature = 'cheok.homepage'

    def _parse(self):
        self._make_want_buy_list_urls()
        self.tasks = self.tasks[:5]

    def _make_want_buy_list_urls(self):
        page_numbers = self._doc.xpath('//*[@class="num"]/text()')
        if len(page_numbers):
            last_page_number = int(page_numbers[-1].encode('utf-8'))
            cur_time = time.time() * 1000
            base_url = 'http://www.cheok.com/interfaces/0/0/0/0/cp_%d?bust=%d'
            tmp = list()
            for page_number in range(1, last_page_number+1):
                url = base_url % (page_number, cur_time)
                task = CrawlTask()
                task.url = url
                task.platform = self.platform
                task.feature = 'cheok.want_buy_list'
                self._md5_mk.update(url)
                task.row_key = self._md5_mk.hexdigest()
                tmp.append(task)
                if page_number % 100 == 0 or page_number == last_page_number:
                    self.tasks.extend(tmp)
                    tmp = list()


def main():
    task = CrawlTask()
    with open('cheok.html', 'r') as f:
        task.__dict__ = {'body': f.read()}
    ret = CheokHomepage(task)
    print(len(ret.tasks))

if __name__ == '__main__':
    main()