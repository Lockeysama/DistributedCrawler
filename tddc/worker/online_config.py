# -*- coding: utf-8 -*-
"""
@author  : chenyitao
@email   : yt.chen@bshier.com
@license: Apache Licence
@software: PyCharm
@file    : online_config.py
@time    : 2018/9/11 11:30
"""
import logging
import sys
from collections import defaultdict

import six

from ..base.util import Singleton, Device
from ..default_config import default_config

from .event import EventCenter
from .redisex import RedisEx
from .models.online_config_model import OnlineConfigEvent
from .models.event_model import Event

log = logging.getLogger(__name__)


@six.add_metaclass(Singleton)
class OnlineConfig(RedisEx):

    _event = {}

    _task = {}

    _redis = {}

    _mysql = {}

    _mongodb = {}

    _proxy = {}

    _extra_modules = defaultdict(dict)

    _template = {}

    def __init__(self):
        super(OnlineConfig, self).__init__()
        log.info('Fetch Online Config.')
        self.first = False
        self.fetch_all()

    def nodes(self, tag):
        return default_config.DEFAULT_REDIS_NODES

    @staticmethod
    @EventCenter.route(OnlineConfigEvent)
    def _config_update_event(event):
        """
        注册到事件中心，在收到相应事件时回调
        :param event:
        :return:
        """
        config_type = event.data.s_type
        ret = OnlineConfig().flush_config(config_type)
        event.set_state(
            Event.Status.Executed_Success if ret else Event.Status.Executed_Failed
        )

    @staticmethod
    def flush_config(target='all'):
        if target == 'all':
            OnlineConfig()._event.clear()
            OnlineConfig()._task.clear()
            OnlineConfig()._redis.clear()
            OnlineConfig()._mysql.clear()
            OnlineConfig()._mongodb.clear()
            OnlineConfig()._proxy.clear()
            OnlineConfig()._extra_modules.clear()
            OnlineConfig().fetch_all()
        elif target == 'event':
            OnlineConfig()._event.clear()
            OnlineConfig().event()
        elif target == 'task':
            OnlineConfig()._task.clear()
            OnlineConfig().task()
        elif target == 'redis':
            OnlineConfig()._redis.clear()
            OnlineConfig().redis()
        elif target == 'mysql':
            OnlineConfig()._mysql.clear()
            OnlineConfig().mysql()
        elif target == 'mongodb':
            OnlineConfig()._mongodb.clear()
            OnlineConfig().mongodb()
        elif target == 'proxy':
            OnlineConfig()._proxy.clear()
            OnlineConfig().proxy()
        elif target == 'extra_modules':
            OnlineConfig()._extra_modules.clear()
            OnlineConfig().extra_modules()
        else:
            return False
        log.info('Fetch {} Config Online.'.format(target.capitalize()))
        return True

    def fetch_config(self, config_type):
        name = 'tddc:worker:config:{platform}:{mac}:{feature}:{type}'.format(
            platform=default_config.PLATFORM.lower(),
            mac=Device.mac(),
            feature=default_config.FEATURE.lower(),
            type=config_type
        )
        record = self.hgetall(name)
        if not record:
            self.first = True
            self.generate_config(config_type)
            record = self.hgetall(name)
        return record

    def fetch_list_of_type_of_config(self, config_type):
        name = 'tddc:worker:config:{platform}:{mac}:{feature}:{type}:*'.format(
            platform=default_config.PLATFORM.lower(),
            mac=Device.mac(),
            feature=default_config.FEATURE.lower(),
            type=config_type
        )
        keys = self.keys(name)
        result = {}
        if not keys:
            self.first = True
            self.generate_list_of_type_of_config(config_type)
            keys = self.keys(name)
        for key in keys:
            record = self.hgetall(key)
            result[key.split(':')[-1]] = record
        return result

    def fetch_list_of_type_of_common_config(self, config_type):
        name = 'tddc:worker:config:common:{type}:{platform}:*'.format(
            platform=default_config.PLATFORM.lower(),
            type=config_type
        )
        keys = self.keys(name)
        result = {}
        if not keys:
            self.first = True
            self.generate_list_of_type_of_common_config(config_type)
            keys = self.keys(name)
            if config_type == 'extra_modules':
                self.first = False
        for key in keys:
            record = self.hgetall(key)
            result[key.split(':')[-1]] = record
        return result

    def fetch_all(self):
        self.event()
        self.task()
        self.redis()
        self.mysql()
        self.mongodb()
        self.proxy()
        self.extra_modules()

    @property
    def event(self):
        if not self._event:
            self._event = self.fetch_list_of_type_of_config('event')
        return type('EventConfig', (), self._event)

    @property
    def task(self):
        if not self._task:
            self._task = self.fetch_list_of_type_of_config('task')
        return type('TaskConfig', (), self._task)

    @property
    def redis(self):
        if not self._redis:
            self._redis = self.fetch_list_of_type_of_config('redis')
        return type('RedisConfig', (), self._redis)

    @property
    def mysql(self):
        if not self._mysql:
            self._mysql = self.fetch_list_of_type_of_config('mysql')
        return type('MySQLConfig', (), self._mysql)

    @property
    def mongodb(self):
        if not self._mongodb:
            self._mongodb = self.fetch_list_of_type_of_config('mongodb')
        return type('MongodbConfig', (), self._mongodb)

    @property
    def proxy(self):
        if not self._proxy:
            self._proxy = self.fetch_list_of_type_of_config('proxy')
        return type('ProxyConfig', (), self._proxy)

    @property
    def extra_modules(self):
        if not self._extra_modules:
            self._extra_modules = self.fetch_list_of_type_of_common_config('extra_modules')
            if self._extra_modules.get('test'):
                if sys.version > '3':
                    self._extra_modules.pop('test')
                else:
                    del self._extra_modules['test']
        return type('ExtraModulesConfig', (), self._extra_modules)

    def generate_config(self, config_type):
        """
        According to the template to generate configuration
        :return:
        """
        config_path_base = 'tddc:worker:config:{platform}:{mac}:{feature}'.format(
            platform=default_config.PLATFORM.lower(),
            mac=Device.mac(),
            feature=default_config.FEATURE.lower()
        ) + ':{}'
        template = self.template.get(config_type)
        if config_type in ('redis', 'mysql', 'mongodb'):
            for k, v in template.items():
                self.hmset(
                    '{}:{}'.format(config_path_base.format(config_type), k), v
                )
        else:
            self.hmset(config_path_base.format(config_type), template)

    def generate_list_of_type_of_config(self, config_type):
        """
        According to the template to generate configuration
        :return:
        """
        config_path_base = 'tddc:worker:config:{platform}:{mac}:{feature}'.format(
            platform=default_config.PLATFORM.lower(),
            mac=Device.mac(),
            feature=default_config.FEATURE.lower()
        ) + ':{}'
        template = self.template.get(config_type)
        for k, v in template.items():
            self.hmset(
                '{}:{}'.format(config_path_base.format(config_type), k), v
            )

    def generate_list_of_type_of_common_config(self, config_type):
        """
        According to the template to generate configuration
        :return:
        """
        config_path_base = 'tddc:worker:config:common:{platform}'.format(
            platform=default_config.PLATFORM.lower(),
        ) + ':{}'
        template = self.template.get(config_type)
        for k, v in template.items():
            self.hmset(
                '{}:{}'.format(config_path_base.format(config_type), k), v
            )

    @property
    def template(self):
        if self._template:
            return self._template
        self._template = {
            'event': {
                'default': {
                    'topic': 'tddc:event:{}'.format(
                        default_config.PLATFORM.lower()
                    ),
                    'record_key': 'tddc:event:record:{}'.format(
                        default_config.PLATFORM.lower()
                    ),
                    'status_key': 'tddc:event:status:{}'.format(
                        default_config.PLATFORM.lower()
                    )
                }
            },
            'task': {
                'default': {
                    'in_queue_topic': 'tddc:task:queue:{}',
                    'out_queue_topic': 'tddc:task:queue:{}',
                    'record_key': 'tddc:task:timing:record',
                    'queue_size': 32
                }
            },
            'redis': {
                'default': {
                    'name': 'default',
                    'host': default_config.DEFAULT_REDIS_NODES[0].get('host'),
                    'port': default_config.DEFAULT_REDIS_NODES[0].get('port'),
                    'password': default_config.DEFAULT_REDIS_NODES[0].get('password') or ''
                }
            },
            'mysql': {
                'default': {
                    'name': 'default',
                    'host': '127.0.0.1',
                    'port': '3306',
                    'user': 'admin',
                    'password': '',
                    'db': 'admin'
                }
            },
            'mongodb': {
                'default': {
                    'name': 'default',
                    'host': '127.0.0.1',
                    'port': '27017',
                    'user': 'admin',
                    'password': '',
                    'db': 'admin'
                }
            },
            'proxy': {
                'default': {
                    'api': '',
                    'source': 'tddc:proxy:source',
                    'pool': 'tddc:proxy:pool'
                }
            },
            'extra_modules': {
                'test': {
                    'owner': 'test',
                    'platform': 'test',
                    'feature': 'test',
                    'package': 'test',
                    'mould': 'test',
                    'version': 'test',
                    'valid': 'test',
                    'timestamp': 'test'
                }
            }
        }
        return self._template
