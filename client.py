# -*- coding: utf-8 -*-
'''
Created on 2017年4月14日

@author: chenyitao
'''

from conf.base_site import MODEL
from common.define import WorkerModel
import multiprocessing


def main():
    if MODEL == WorkerModel.PARSER:
        from worker.parser.parser import Parser
        Parser.start()
    elif MODEL == WorkerModel.CRAWLER:
        from worker.crawler.crawler import Crawler
        Crawler.start()
    elif MODEL == WorkerModel.PROXY_CHECKER:
        from worker.proxy_checker.proxy_checker import ProxyChecker
        from worker.proxy_checker.proxy_src_updater import ProxySourceUpdater
        def update_ip_source():
            ProxySourceUpdater().start()
        multiprocessing.Process(target=update_ip_source).start()
        ProxyChecker.start()
        
        
        
    
if __name__ == '__main__':
    main()
