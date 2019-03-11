# -*- coding: utf-8 -*-
"""
Created on 2017年4月14日

@author: chenyitao
"""
import logging

from tddc.worker import Worker, KeepTaskManager

log = logging.getLogger(__name__)


class KeepCrawlerWorker(Worker):
    """
    classdocs
    """

    def plugins(self):
        return (
            (KeepTaskManager, None, None),
        )


def main():
    KeepCrawlerWorker.start()


if __name__ == '__main__':
    main()
