# -*- coding: utf-8 -*-
"""
@author  : chenyitao
@email   : yt.chen@bshier.com
@license: Apache Licence
@software: PyCharm
@file    : request.py
@time    : 2018/7/30 18:07
"""
import random

import gevent

from tddc.worker.models.timing_task_model import TimingTaskStatus

from .proxy import ProxyHelper


class Response(object):

    def __init__(self, task, request, response):
        if self._check(response):
            task.i_state = TimingTaskStatus.CrawledSuccess
            task.s_cache = response.text
            if task.s_proxy and task.s_proxy.lower() in ['http', 'https'] and request.proxies:
                gevent.spawn_later(
                    random.uniform(2, 4),
                    ProxyHelper.give_back_proxy(task.s_platform, request.proxies)
                )
        else:
            task.i_state = response.status_code

    def _check(self, response):
        return response.status_code == 200
