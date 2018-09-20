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
import gevent.monkey; gevent.monkey.patch_all()
import gevent
from tddc.worker import logging_ext; logging_ext.patch()

from ..config import default_config
from ..util.util import Singleton

from .register import Register
from .online_config import OnlineConfig


class Worker(object):

    __metaclass__ = Singleton

    def __init__(self):
        super(Process, self).__init__()
        setproctitle.setproctitle(default_config.PLATFORM)
        Register()
        OnlineConfig()
        self.worker_cls()()
        while True:
            gevent.sleep(100)

    def worker_cls(self):
        raise NotImplementedError
