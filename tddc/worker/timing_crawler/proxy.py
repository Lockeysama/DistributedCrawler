# -*- coding: utf-8 -*-
"""
@author  : chenyitao
@email   : yt.chen@bshier.com
@license: Apache Licence
@software: PyCharm
@file    : proxy.py
@time    : 2018/8/1 15:52
"""

from ..redisex import RedisEx
from ..online_config import OnlineConfig


class NoProxyException(Exception):

    def __init__(self, task):
        err_msg = '[{}:{}:{}][{}] No Proxy.'.format(
            task.s_platform, task.s_feature, task.s_url, 'NoProxyException'
        )
        super(NoProxyException, self).__init__(err_msg)


class ProxyHelper(object):

    def __init__(self):
        self.conf = type('ProxyConfig', (), OnlineConfig().proxy.default)

    @classmethod
    def to_borrow_proxy(cls, task):
        if task.s_proxy != 'None':
            if task.s_proxy.lower() in ['http', 'https']:
                ip_port = RedisEx().get_random('{}:{}'.format(
                    ProxyHelper.conf.pool, task.s_platform)
                )
                if not ip_port:
                    ip_port = RedisEx().get_random('{}:{}'.format(
                        ProxyHelper.conf.source, task.s_proxy.lower()), False
                    )
                    if not ip_port:
                        raise NoProxyException(task)
                return ip_port
            else:
                proxy_info = task.s_proxy.split('://')
                proxies = proxy_info[1] if len(proxy_info) == 2 else proxy_info[0]
                return proxies
        else:
            return None

    @classmethod
    def give_back_proxy(cls, platform, proxies):
        RedisEx().set('{}:{}'.format(
            ProxyHelper.conf.pool, platform), proxies
        )
