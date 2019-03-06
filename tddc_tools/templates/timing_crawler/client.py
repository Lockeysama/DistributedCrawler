# -*- coding: utf-8 -*-
"""
Created on 2017年4月14日

@author: chenyitao
"""
import logging

from tddc.worker import Worker, TimingCrawler

log = logging.getLogger(__name__)


class CrawlerManager(Worker):
    """
    classdocs
    """

    def plugins(self):
        return (
            (TimingCrawler, None, None),
        )


def main():
    CrawlerManager.start()


if __name__ == '__main__':
    main()
