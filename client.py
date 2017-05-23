# -*- coding: utf-8 -*-
'''
Created on 2017年4月14日

@author: chenyitao
'''

import multiprocessing
import gevent.monkey
gevent.monkey.patch_all()

from conf.base_site import WorkerModel, MODEL


def main():
    if MODEL == WorkerModel.Parser:
        from worker.parser.parser_manager import ParserManager
        ParserManager.start()
    elif MODEL == WorkerModel.Crawler:
        from worker.crawler.crawler_manager import CrawlerManager
        CrawlerManager.start()
    elif MODEL == WorkerModel.ProxyChecker:
        from worker.proxy_checker.proxy_checker import ProxyChecker
        from worker.proxy_checker.proxy_src_updater import ProxySourceUpdater
        def update_ip_source():
            ProxySourceUpdater().start()
        multiprocessing.Process(target=update_ip_source).start()
        ProxyChecker.start()
    elif MODEL == WorkerModel.Monitor:
        from worker.monitor.monitor_manager import MonitorManager
        MonitorManager.start()


if __name__ == '__main__':
    main()
