# -*- coding: utf-8 -*-
"""
@author  : miaokaixiao
@email   : yt.chen@bshier.com
@license: Apache Licence
@software: PyCharm
@file    : downloader.py
@time    : 2018/10/10 16:35
"""
import logging
import gevent
import requests
from gevent.pool import Pool

from ..online_config import OnlineConfig
from ..extern_modules import ExternManager
from ..extern_modules.proxies_checker.response import ResponseExtra
from ..extern_modules.proxies_checker.request import RequestExtra

logging.getLogger('urllib3').setLevel(logging.WARNING)
log = logging.getLogger(__name__)


class Downloader(object):
    def __init__(self, concurrent=64):
        self.proxy_conf = OnlineConfig().proxy
        self.pool = Pool(concurrent)
        self.pool.join()

    def add_task(self, task, proxy):
        self.pool.add(gevent.spawn(self._download, task, proxy))

    def free_count(self):
        return self.pool.free_count()

    @staticmethod
    def _before_download(task, proxy):
        module = ExternManager().get_model(task.s_platform, task.s_feature + '.request')
        request = module(task, proxy) if module else RequestExtra(task, proxy)
        return request

    @staticmethod
    def _after_download(task, request, response, proxy):
        module = ExternManager().get_model(task.s_platform, task.s_feature + '.response')
        response = module(task, request, response, proxy) \
            if module else ResponseExtra(task, request, response, proxy)
        return response

    def _download(self, task, proxy):
        request = None
        req_response = None
        try:
            request = self._before_download(task, proxy)
            req_response = requests.request(**request())
            response = self._after_download(task, request, req_response, proxy)
            del response
            del req_response
            del request
        except Exception as e:
            if req_response:
                del req_response
            if request:
                del request
        finally:
            del task
            del proxy
