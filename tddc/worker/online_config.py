# -*- coding: utf-8 -*-
"""
@author  : chenyitao
@email   : yt.chen@bshier.com
@license: Apache Licence
@software: PyCharm
@file    : online_config.py
@time    : 2018/9/11 11:30
"""
import json
import logging
from string import lower

from ..redis.redis_client import RedisClient
from ..util.util import Singleton
from ..config import default_config

from .authorization import Authorization
from .event import EventCenter, Event

log = logging.getLogger(__name__)


class OnlineConfig(RedisClient):

    __metaclass__ = Singleton

    _event = {}

    _task = {}

    _redis = {}

    _mysql = {}

    _mongodb = {}

    _proxy = {}

    _template = {}

    def __init__(self):
        nodes = [{'host': node.get('host'),
                  'port': node.get('port')}
                 for node in default_config.AUTH_REDIS_NODES]
        super(OnlineConfig, self).__init__(startup_nodes=nodes)
        log.info('Fetch Online Config.')
        self.first = False
        self.fetch_all()

    @staticmethod
    @EventCenter.route(Event.Type.OnlineConfigFlush)
    def flush_config(event):
        target = event.event.get('target')
        if not target:
            return
        target = lower(target)
        if target == 'all':
            OnlineConfig()._event.clear()
            OnlineConfig()._task.clear()
            OnlineConfig()._redis.clear()
            OnlineConfig()._mysql.clear()
            OnlineConfig()._mongodb.clear()
            OnlineConfig()._proxy.clear()
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
        else:
            return
        log.info('Fetch {} Config Online.'.format(target.capitalize()))

    def fetch_config(self, config_type):
        name = 'tddc:worker:config:{platform}:{ip}:{feature}:{type}'.format(
            platform=lower(Authorization().register_info.get('platform')),
            ip=Authorization().register_info.get('ip'),
            feature=lower(Authorization().register_info.get('feature')),
            type=config_type
        )
        record = self.hgetall(name)
        if not record:
            self.first = True
            self.generate_config(config_type)
            record = self.hgetall(name)
        return record

    def fetch_list_of_type_of_config(self, config_type):
        name = 'tddc:worker:config:{platform}:{ip}:{feature}:{type}:*'.format(
            platform=lower(Authorization().register_info.get('platform')),
            ip=Authorization().register_info.get('ip'),
            feature=lower(Authorization().register_info.get('feature')),
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

    def fetch_all(self):
        self.event()
        self.task()
        self.redis()
        self.mysql()
        self.mongodb()
        self.proxy()

    @property
    def event(self):
        if not self._event:
            self._event = self.fetch_config('event')
        return type('EventConfig', (), self._event)

    @property
    def task(self):
        if not self._task:
            self._task = self.fetch_config('task')
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
            self._proxy = self.fetch_config('proxy')
        return type('ProxyConfig', (), self._proxy)

    def generate_config(self, config_type):
        """
        According to the template to generate configuration
        :return:
        """
        config_path_base = 'tddc:worker:config:{platform}:{ip}:{feature}'.format(
            platform=lower(Authorization().register_info.get('platform')),
            ip=Authorization().register_info.get('ip'),
            feature=lower(Authorization().register_info.get('feature'))
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
        config_path_base = 'tddc:worker:config:{platform}:{ip}:{feature}'.format(
            platform=lower(Authorization().register_info.get('platform')),
            ip=Authorization().register_info.get('ip'),
            feature=lower(Authorization().register_info.get('feature'))
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
                'topic': 'tddc:event:{}'.format(
                    lower(Authorization().register_info.get('platform'))
                ),
                'record_key': 'tddc:event:record:{}'.format(
                    lower(Authorization().register_info.get('platform'))
                ),
                'status_key': 'tddc:event:status:{}'.format(
                    lower(Authorization().register_info.get('platform'))
                )
            },
            'task': {
                'in_queue_topic': 'tddc:task:queue:{}',
                'out_queue_topic': 'tddc:task:queue:{}',
                'cache_key': 'tddc:task:cache',
                'status_key': 'tddc:task:status',
                'record_key': 'tddc:task:record',
                'queue_size': 32
            },
            'redis': {
                'default': {
                    'name': 'default',
                    'host': default_config.ONLINE_CONFIG_REDIS_NODES[0].get('host'),
                    'port': default_config.ONLINE_CONFIG_REDIS_NODES[0].get('port'),
                    'password': default_config.ONLINE_CONFIG_REDIS_NODES[0].get('password') or ''
                }
            },
            'mysql': {
                'default': {
                    'name': 'default',
                    'host': '127.0.0.1',
                    'port': '6379',
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
                'source': 'tddc:proxy:source',
                'pool': 'tddc:proxy:pool'
            }
        }
        return self._template
