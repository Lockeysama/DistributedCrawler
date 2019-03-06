# -*- coding: utf-8 -*-
"""
@author  : chenyitao
@email   : yt.chen@bshier.com
@license: Apache Licence
@software: PyCharm
@file    : device_info.py
@time    : 2018/9/10 18:10
"""
import gevent
import psutil
import socket
import netifaces


class Device(object):

    _ip = None

    _mac = None

    @classmethod
    def ip(cls):
        if cls._ip:
            return cls._ip
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        except:
            ip = None
        finally:
            s.close()
        cls._ip = ip
        return ip

    @classmethod
    def mac(cls):
        if cls._mac:
            return cls._mac
        for i in netifaces.interfaces():
            address = netifaces.ifaddresses(i)
            try:
                if_mac = address[netifaces.AF_LINK][0]['addr']
                if_ip = address[netifaces.AF_INET][0]['addr']
            except Exception as e:
                continue
            if if_ip == Device.ip():
                cls._mac = if_mac.replace(':', '-')
                return cls._mac
        return None

    @classmethod
    def process_snapshot(cls):
        snapshot = []
        for p in psutil.process_iter():
            try:
                snapshot.append({
                    'pid': p.pid,
                    'name': p.name(),
                    'cpu_percent': p.cpu_percent(),
                    'rss': float('%.2f' % (p.memory_info().rss / 1024 / 1024)),
                    'memory_percent': float('%.2f' % (p.memory_percent() * 100))
                })
            except Exception as e:
                pass
        return snapshot

    @classmethod
    def cpu_snapshot(cls):
        return {
            'cpu_count': psutil.cpu_count(),
            'cpu_percent': psutil.cpu_percent(1, True)
        }

    @classmethod
    def memory_snapshot(cls):
        mem = psutil.virtual_memory()
        return {
            'mem_total': float('%.2f' % (mem.total / 1073741824.0)),
            'mem_used': float('%.2f' % (mem.used / 1073741824.0)),
            'mem_available': float('%.2f' % (mem.available / 1073741824.0)),
            'mem_percent': mem.percent
        }

    @classmethod
    def disk_snapshot(cls):
        disk = psutil.disk_usage('/')
        return {
            'disk_total': float('%.2f' % (disk.total / 1073741824.0)),
            'disk_used': float('%.2f' % (disk.used / 1073741824.0)),
            'disk_free': float('%.2f' % (disk.free / 1073741824.0)),
            'disk_percent': disk.percent
        }

    @classmethod
    def net_snapshot(cls):
        net_io_counters = psutil.net_io_counters()
        return {
            'send': net_io_counters.bytes_sent,
            'recv': net_io_counters.bytes_recv
        }

    @classmethod
    def net_rate(cls, interval=1):
        old = Device.net_snapshot()
        gevent.sleep(interval)
        new = Device.net_snapshot()
        rate = {}
        for k, v in new.items():
            rate[k] = float('%.2f' % ((v - old[k]) / 1024.0 / 1024))
        return rate
