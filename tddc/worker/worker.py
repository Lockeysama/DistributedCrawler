# -*- coding: utf-8 -*-
"""
@author  : chenyitao
@email   : yt.chen@bshier.com
@license: Apache Licence
@software: PyCharm
@file    : process.py
@time    : 2018/9/11 11:24
"""
import setproctitle
import gevent.monkey
import logging

import gevent
import logging_ext

from ..config import default_config
from ..util.util import Singleton

from .authorization import Authorization
from .online_config import OnlineConfig
from .monitor import Monitor

log = logging.getLogger(__name__)


class Worker(object):

    __metaclass__ = Singleton

    def __init__(self):
        super(Worker, self).__init__()
        setproctitle.setproctitle(default_config.PLATFORM)
        gevent.monkey.patch_all()
        logging_ext.patch()
        log.info('{} Is Start.'.format(default_config.PLATFORM))
        Authorization()
        if not Authorization().logged:
            return
        OnlineConfig()
        if OnlineConfig().first:
            return
        Monitor()
        self._start_plugins()

    @classmethod
    def start(cls):
        cls()
        log.info('{} Is Running.'.format(default_config.PLATFORM))
        while Authorization().logged and not OnlineConfig().first:
            gevent.sleep(10)
        if not Authorization().logged:
            log.error('Process Exit(Authorization Failed).')
        elif OnlineConfig().first:
            log.error('Process Exit(Online Config Must Be Edit).')

    def _start_plugins(self):
        for plugin_cls, args, kwargs in self.plugins():
            if not plugin_cls:
                continue
            if not args and not kwargs:
                plugin_cls()
            elif args and not kwargs:
                plugin_cls(*args)
            elif not args and kwargs:
                plugin_cls(**kwargs)
            else:
                plugin_cls(*args, **kwargs)

    def plugins(self):
        raise NotImplementedError
