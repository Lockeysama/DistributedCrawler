# -*- coding: utf-8 -*-
'''
Created on 2017年4月14日

@author: chenyitao
'''

import multiprocessing
import gevent.monkey
gevent.monkey.patch_all()


def main():
    import settings
    settings.WORKER = settings.Worker.Monitor
    if settings.WORKER == settings.Worker.Parser:
        from worker.parser.manager import ParserManager
        ParserManager.start()
    elif settings.WORKER == settings.Worker.Crawler:
        from worker.crawler.manager import CrawlerManager
        CrawlerManager.start()
    elif settings.WORKER == settings.Worker.ProxyChecker:
        from worker.proxy_checker.manager import ProxyCheckerManager
        from worker.proxy_checker.src_proxies_updater import ProxySourceUpdater
        def update_ip_source():
            ProxySourceUpdater().start()
        from conf.proxy_checker_site import ProxyCheckerSite
        if ProxyCheckerSite.PROXY_SOURCE_UPDATER_ENABLE:
            multiprocessing.Process(target=update_ip_source).start()
        ProxyCheckerManager.start()
    elif settings.WORKER == settings.Worker.Monitor:
        from worker.monitor.manager import MonitorManager
        MonitorManager.start()


if __name__ == '__main__':
    main()
