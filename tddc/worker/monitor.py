# -*- coding: utf-8 -*-
"""
@author  : chenyitao
@email   : yt.chen@bshier.com
@license: Apache Licence
@software: PyCharm
@file    : monitor.py
@time    : 2018/9/18 10:54
"""
import json
import time

import gevent

from ..util.time_helper import TimeHelper
from ..util.device_info import Device
from ..util.util import Singleton

from .status import StatusManager


class Monitor(object):

    __metaclass__ = Singleton

    def __init__(self):
        gevent.spawn(self.snapshot)
        gevent.sleep()
        gevent.spawn(self.cpu_usage_rate)
        gevent.sleep()
        gevent.spawn(self.memory_usage_rate)
        gevent.sleep()
        gevent.spawn(self.net_usage_rate)
        gevent.sleep()

    @staticmethod
    def snapshot():
        name = 'tddc:worker:monitor:snapshot:{}'.format(Device.ip())
        while True:
            min_ts = TimeHelper(time.time()).get_minute_timestamp()
            date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(min_ts))
            process_snapshot = Device.process_snapshot()
            disk_snapshot = Device.disk_snapshot()
            cpu_snapshot = Device.cpu_snapshot()
            memory_snapshot = Device.memory_snapshot()
            StatusManager().hmset(
                name, {
                    'process': json.dumps(process_snapshot),
                    'disk': json.dumps(disk_snapshot),
                    'cpu': json.dumps(cpu_snapshot),
                    'memory': json.dumps(memory_snapshot),
                    'date': date
                }
            )
            gevent.sleep(60)

    @staticmethod
    def cpu_usage_rate():
        name = 'tddc:worker:monitor:cpu_usage_rate:{}'.format(Device.ip())
        while True:
            min_ts = TimeHelper(time.time()).get_minute_timestamp()
            date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(min_ts))
            snapshot = Device.cpu_snapshot()
            snapshot['date'] = date
            StatusManager().hmset(name, {min_ts: json.dumps(snapshot)})
            keys = StatusManager().hkeys(name)
            if len(keys) > 1450:
                keys.sort()
                expire = keys[:len(keys) - 1440]
                StatusManager().hmdel(name, expire)
            gevent.sleep(60)

    @staticmethod
    def memory_usage_rate():
        name = 'tddc:worker:monitor:memory_usage_rate:{}'.format(Device.ip())
        while True:
            min_ts = TimeHelper(time.time()).get_minute_timestamp()
            date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(min_ts))
            snapshot = Device.memory_snapshot()
            snapshot['date'] = date
            StatusManager().hmset(name, {min_ts: json.dumps(snapshot)})
            keys = StatusManager().hkeys(name)
            if len(keys) > 1450:
                keys.sort()
                expire = keys[:len(keys) - 1440]
                StatusManager().hmdel(name, expire)
            gevent.sleep(60)

    @staticmethod
    def net_usage_rate():
        name = 'tddc:worker:monitor:net_usage_rate:{}'.format(Device.ip())
        while True:
            net_rate = Device.net_rate(60)
            min_ts = TimeHelper(time.time()).get_minute_timestamp()
            date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(min_ts))
            net_rate['date'] = date
            StatusManager().hmset(name, {min_ts: json.dumps(net_rate)})
            keys = StatusManager().hkeys(name)
            if len(keys) > 1450:
                keys.sort()
                expire = keys[:len(keys) - 1440]
                StatusManager().hmdel(name, expire)
            gevent.sleep(60)
