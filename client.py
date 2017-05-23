# -*- coding: utf-8 -*-
'''
Created on 2017年4月14日

@author: chenyitao
'''

import multiprocessing
import gevent.monkey
from conf.proxy_checker_site import ProxyCheckerSite
gevent.monkey.patch_all()

from conf import Worker, BaseSite


def main():
    if BaseSite.WORKER == Worker.Parser:
        from worker.parser.parser_manager import ParserManager
        ParserManager.start()
    elif BaseSite.WORKER == Worker.Crawler:
        from worker.crawler.crawler_manager import CrawlerManager
        CrawlerManager.start()
    elif BaseSite.WORKER == Worker.ProxyChecker:
        from worker.proxy_checker.manager import ProxyCheckerManager
        from worker.proxy_checker.src_proxies_updater import ProxySourceUpdater
        def update_ip_source():
            ProxySourceUpdater().start()
        if ProxyCheckerSite.PROXY_SOURCE_UPDATER_ENABLE:
            multiprocessing.Process(target=update_ip_source).start()
        ProxyCheckerManager.start()
    elif BaseSite.WORKER == Worker.Monitor:
        from worker.monitor.monitor_manager import MonitorManager
        MonitorManager.start()


if __name__ == '__main__':
    main()
