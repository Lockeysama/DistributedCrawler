# -*- coding: utf-8 -*-
"""
Created on 2017年4月17日

@author: chenyitao
"""
import base64
import logging
import time

import requests
import setproctitle
import json
from os import getpid
import socket

import gevent.pool

from ...default_config import default_config

from ..online_config import OnlineConfig
from ..redisex import RedisEx

from .downloader import Downloader

log = logging.getLogger(__name__)


class ProxiesChecker(object):
    """
    代理更新控制
    """

    HTTP_CHECK_CONCURRENT = 32

    HTTPS_CHECK_CONCURRENT = 32

    REPEATED_INTERVAL = 1800

    REPEATED_CONCURRENT = 32

    def __init__(self):
        super(ProxiesChecker, self).__init__()
        log.info('Checker Is Starting.')
        self.proxy_conf = type('ProxyConfig', (), OnlineConfig().proxy.default)
        self._rules_moulds = {'http': {}, 'https': {}}
        self.main_pid = getpid()
        pid = gevent.fork()
        if pid:
            gevent.spawn(self._fetch_source_proxy)
            gevent.sleep()
            gevent.spawn(self._check, self.HTTP_CHECK_CONCURRENT, 'http')
            gevent.sleep()
            gevent.spawn(self._check, self.HTTPS_CHECK_CONCURRENT, 'https')
            gevent.sleep()
            log.info('Checker Was Started.')
            gevent.spawn(self._pull_check_list)
            gevent.sleep()
        else:
            self._regular_run()

    def _fetch_source_proxy(self):
        def _parse_kuaidaili(data):
            proxies = {'HTTP': [], 'HTTPS': []}
            infos = json.loads(data)
            if infos.get('code'):
                return proxies
            proxy_list = infos.get('data').get('proxy_list', [])
            for proxy_info in proxy_list:
                proxy, proxy_type = proxy_info.split(',')
                proxies[proxy_type].append(proxy)
            return proxies

        def _proxy_active_check(ips):
            active_ips = []

            def _checker(ip):
                try:
                    _ip, _port = ip.split(':')
                    _s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    _s.settimeout(5)
                    _s.connect((_ip, int(_port)))
                    _s.close()
                except:
                    pass
                else:
                    active_ips.append(ip)

            p = gevent.pool.Pool(self.REPEATED_CONCURRENT)
            p.map(_checker, ips)
            p.join()
            return active_ips

        while True:
            http_count = RedisEx().scard('{}:http'.format(self.proxy_conf.source))
            https_count = RedisEx().scard('{}:https'.format(self.proxy_conf.source))
            if http_count < 100 or https_count < 100:
                try:
                    url = self.proxy_conf.api
                    url = base64.b64decode(url)
                    rsp = requests.get(url, timeout=5)
                    if rsp.status_code == 200:
                        proxies = _parse_kuaidaili(rsp.content)
                        active_proxies = _proxy_active_check(proxies.get('HTTP'))
                        RedisEx().smadd('{}:http'.format(self.proxy_conf.source), active_proxies)
                        log.info('Fetch({}) HTTP Proxies.'.format(len(active_proxies)))
                        active_proxies = _proxy_active_check(proxies.get('HTTPS'))
                        RedisEx().smadd('{}:https'.format(self.proxy_conf.source), active_proxies)
                        log.info('Fetch({}) HTTPS Proxies.'.format(len(active_proxies)))
                except Exception as e:
                    log.exception(e)
            gevent.sleep(2)

    def _pull_check_list(self):
        while True:
            keys = RedisEx().keys('tddc:worker:config:common:proxy_check_list:*')
            items = [RedisEx().hgetall(key) for key in keys]
            items = [type('ProxyItem', (), item) for item in items
                     if item and item.get('s_platform') and item.get('s_feature')
                     and item.get('s_url') and item.get('b_valid')]
            _rules_moulds = {'http': {}, 'https': {}}
            if len(items):
                for item in items:
                    _rules_moulds[item.s_proxy.lower()][item.s_platform] = item
                log.info('Proxy Checker Running({}).'.format(len(items)))
            self._rules_moulds = _rules_moulds
            gevent.sleep(15)

    def _check(self, concurrent, proxy_type):
        cnt = 0
        _spider = Downloader(concurrent)
        gevent.sleep(5)
        while True:
            try:
                if not len(self._rules_moulds[proxy_type]):
                    gevent.sleep(5)
                    continue
                if _spider.free_count() <= 0:
                    gevent.sleep(1)
                    continue
                proxy = RedisEx().get_random('{}:{}'.format(self.proxy_conf.source, proxy_type))
                if not proxy:
                    if not cnt % 6:
                        log.warning('No Proxy(%s).' % proxy_type)
                    cnt += 1
                    gevent.sleep(5)
                    continue
                for _, item in self._rules_moulds[proxy_type].items():
                    _spider.add_task(item, proxy)
            except Exception as e:
                log.exception(e)

    def _regular_run(self):
        setproctitle.setproctitle('TDDC-ProxyAliveCheck-{}'.format(default_config.FEATURE))
        log.info('Proxy Alive Check Is Running.')
        pool = gevent.pool.Pool(self.REPEATED_CONCURRENT)
        gevent.sleep(5)
        while True:
            keys = RedisEx().keys('tddc:worker:config:common:proxy_check_list:*')
            items = [RedisEx().hgetall(key) for key in keys]
            platforms = {item.get('s_platform') for item in items
                         if item and item.get('s_platform') and item.get('s_feature')
                         and item.get('s_url') and item.get('b_valid')}
            pre_timestamp = RedisEx().hgetall('tddc:proxy:repeated')
            ts = int(time.time())
            for platform in platforms:
                if ts - int(pre_timestamp.get(platform, 0)) < self.REPEATED_INTERVAL:
                    continue
                coroutines = [
                    pool.spawn(self._check_handle, self.proxy_conf.pool, platform, proxy)
                    for proxy in RedisEx().smembers('{}:{}'.format(self.proxy_conf.pool, platform))
                ]
                gevent.joinall(coroutines)
                RedisEx().hset('tddc:proxy:repeated', platform, ts)
            for http_type in ['http', 'https']:
                if ts - int(pre_timestamp.get(http_type, 0)) < self.REPEATED_INTERVAL:
                    continue
                coroutines = [
                    pool.spawn(self._check_handle, self.proxy_conf.source, http_type, proxy)
                    for proxy in RedisEx().smembers('{}:{}'.format(self.proxy_conf.source, http_type))
                ]
                gevent.joinall(coroutines)
                RedisEx().hset('tddc:proxy:repeated', http_type, ts)
            gevent.sleep(10)

    def _check_handle(self, key_base, platform, ip):
        try:
            _ip, _port = ip.split(':')
            _s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            _s.settimeout(5)
            _s.connect((_ip, int(_port)))
            _s.close()
        except:
            RedisEx().srem('{}:{}'.format(key_base, platform), ip)
            log.info('[{}:{}] Was Removed'.format(platform, ip))
