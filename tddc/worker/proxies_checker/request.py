# -*- coding: utf-8 -*-
"""
@author  : chenyitao
@email   : yt.chen@bshier.com
@license: Apache Licence
@software: PyCharm
@file    : request.py
@time    : 2018/10/10 18:07
"""
import json
import random
import sys


class Request(object):

    default_headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
        'DNT': '1',
        'Upgrade-Insecure-Requests': '1'
    }

    user_agents = [('Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) '
                    'Chrome/41.0.2228.0 Safari/537.36'),
                   ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) '
                    'Chrome/41.0.2227.1 Safari/537.36'),
                   ('Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) '
                    'Chrome/40.0.2214.93 Safari/537.36'),
                   'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1',
                   'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0',
                   'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko',
                   'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)',
                   ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                    'Chrome/42.0.2311.135 Safari/537.36 Edge/12.246'),
                   ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) '
                    'Version/7.0.3 Safari/7046A194A'),
                   ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/602.1.50 (KHTML, like Gecko) '
                    'Version/10.0 Safari/602.1.50')]

    def __init__(self, task, proxy):
        self.method = task.s_method or 'get'
        self.url = task.s_url
        self.headers = self.make_headers(task)
        self.params = getattr(task, 's_params', None)
        self.data = getattr(task, 's_data', None)
        self.json = getattr(task, 's_json', None)
        self.cookies = getattr(task, 's_cookies', None)
        self.proxies = proxy
        self.timeout = int(getattr(task, 'i_timeout', 5))

    def make_headers(self, task):
        headers = json.loads(task.s_headers) \
            if hasattr(task, 's_headers') and task.s_headers \
            else {}
        headers['User-Agent'] = headers.get('User-Agent', self._user_agent())
        for key, value in self.default_headers.items():
            headers[key] = headers.get(key, value)
        for key in headers.copy():
            if 'custom' in key:
                if sys.version > '3':
                    headers.pop(key)
                else:
                    del headers[key]
        return headers

    @staticmethod
    def _user_agent():
        return random.choice(Request.user_agents)

    def __call__(self, *args, **kwargs):
        kwargs = {
            'timeout': self.timeout, 'method': self.method,
            'url': self.url, 'headers': self.headers, 'cookies': self.cookies, 'params': self.params,
            'data': self.data, 'json': self.json,
        }
        if self.proxies:
            kwargs['proxies'] = {
                'http': 'http://{}'.format(self.proxies),
                'https': 'https://{}'.format(self.proxies)
            }
        for key, value in kwargs.copy().items():
            if not value:
                if sys.version > '3':
                    kwargs.pop(key)
                else:
                    del kwargs[key]
        return kwargs
