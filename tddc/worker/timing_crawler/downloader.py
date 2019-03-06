# -*- coding: utf-8 -*-
"""
@author  : chenyitao
@email   : yt.chen@bshier.com
@license: Apache Licence
@software: PyCharm
@file    : downloader.py
@time    : 2018/7/30 16:35
"""
import logging
import gevent
import requests
from gevent.pool import Pool
import requests.exceptions as exceptions

from ..extern_modules import ExternManager
from ..timing_task_manager import TimingTaskStatus
from ..extern_modules.timing_crawler.request import RequestExtra
from ..extern_modules.timing_crawler.response import ResponseExtra

from .proxy import NoProxyException

log = logging.getLogger(__name__)


class SpiderBase(object):

    def task_failed(self, task):
        raise NotImplementedError

    def task_success(self, task):
        raise NotImplementedError

    def task_wait(self, task):
        raise NotImplementedError


class Downloader(object):

    def __init__(self, callback_cls, concurrent=64):
        self.callback = callback_cls
        self.pool = Pool(concurrent)
        self.pool.join()

    def add_task(self, task):
        log.debug('[{}][{}][{}] Add New Task.'.format(
            task.s_platform, task.s_feature, task.s_url)
        )
        self.pool.add(gevent.spawn(self._download, task))

    @staticmethod
    def _before_download(task):
        module = ExternManager().get_model(
            task.s_platform, task.s_feature + '.request'
        )
        request = module(task) if module else RequestExtra(task)
        return request

    @staticmethod
    def _after_download(task, request, response):
        module = ExternManager().get_model(
            task.s_platform, task.s_feature + '.response'
        )
        response = module(task, request, response) \
            if module else ResponseExtra(task, request, response)
        return response

    def _download(self, task, retry=5):
        if retry == 0:
            return self.callback.task_failed(task)
        elif retry != 5:
            log.warning('[{}:{}:{}] Retry({}).'.format(
                task.s_platform, task.s_feature, task.s_url, retry)
            )
        err_msg_fmt = '[{}:{}:{}]'.format(
            task.s_platform, task.s_feature, task.s_url
        ) + '[{}] {}.'
        request = None
        response = None
        req_response = None
        try:
            request = self._before_download(task)
            req_response = requests.request(**request())
            response = self._after_download(task, request, req_response)
        except NoProxyException as e:
            log.warning(e)

            def _wait():
                self.callback.task_wait(task)

            return gevent.spawn_later(15, _wait)
        except requests.ConnectTimeout as e:
            log.warning(err_msg_fmt.format(e.__class__.__name__, e.args))
            return self._download(task, retry)
        except requests.HTTPError as e:
            log.warning(err_msg_fmt.format(e.__class__.__name__, e.args))
            return self._download(task, retry - 1)
        except requests.TooManyRedirects as e:
            log.warning(err_msg_fmt.format(e.__class__.__name__, e.args))
            return self._download(task, retry - 1)
        except requests.URLRequired as e:
            log.warning(err_msg_fmt.format(e.__class__.__name__, e.args))
            return self._download(task, retry - 1)
        except exceptions.ProxyError as e:
            log.warning(err_msg_fmt.format(e.__class__.__name__, e.args))
            return self._download(task, retry)
        except exceptions.ReadTimeout as e:
            log.warning(err_msg_fmt.format(e.__class__.__name__, e.args))
            return self._download(task, retry - 1)
        except exceptions.ConnectionError as e:
            log.warning(err_msg_fmt.format(e.__class__.__name__, e.args))
            return self._download(task, retry - 1)
        except Exception as e:
            log.warning(err_msg_fmt.format(e.__class__.__name__, e.args))
            return self._download(task, retry - 1)
        finally:
            if request:
                del request
            if response:
                del response
            if req_response:
                del req_response
        if task.i_state == TimingTaskStatus.CrawledSuccess:
            return self.callback.task_success(task)
        elif task.i_state == TimingTaskStatus.WaitCrawl:
            return self._download(task, retry - 1)
        elif task.i_state >= 400:
            if task.i_state == 403:
                return self._download(task, retry)
            return self._download(task, retry - 1)
        else:
            return self.callback.task_failed(task)
