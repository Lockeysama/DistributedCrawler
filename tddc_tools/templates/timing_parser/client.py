# -*- coding: utf-8 -*-
"""
Created on 2017年4月14日

@author: chenyitao
"""
import logging

from tddc.worker import Worker, TimingParser

log = logging.getLogger(__name__)


class ParserManager(Worker):

    def plugins(self):
        return (
            (TimingParser, None, None),
        )


def main():
    ParserManager.start()


if __name__ == '__main__':
    main()
