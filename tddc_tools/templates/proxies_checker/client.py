# -*- coding: utf-8 -*-
"""
Created on 2017年4月14日

@author: chenyitao
"""
import logging

from tddc.worker import Worker, ProxiesChecker

log = logging.getLogger(__name__)


class ProxyCheckerManager(Worker):
    """
    classdocs
    """

    def plugins(self):
        return (
            (ProxiesChecker, None, None),
        )


def main():
    ProxyCheckerManager.start()


if __name__ == '__main__':
    main()
