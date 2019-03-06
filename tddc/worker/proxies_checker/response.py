# -*- coding: utf-8 -*-
"""
@author  : chenyitao
@email   : yt.chen@bshier.com
@license: Apache Licence
@software: PyCharm
@file    : request.py
@time    : 2018/7/30 18:07
"""
import logging

from ..online_config import OnlineConfig
from ..redisex import RedisEx

log = logging.getLogger(__name__)


class Response(object):

    def __init__(self, task, request, response, proxy):
        self.request = request
        self.response = response
        self.proxy_conf = type('ProxyConfig', (), OnlineConfig().proxy.default)

        if self._check(response):
            RedisEx().set(
                '{}:{}'.format(self.proxy_conf.pool, task.s_platform),
                proxy
            )
            log.debug('[{}:{}:{}]'.format(task.s_proxy, task.s_platform, proxy))

    def _check(self, response):
        return response.status_code == 200
