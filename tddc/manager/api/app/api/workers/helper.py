# -*- coding: utf-8 -*-
"""
@author  : chenyitao
@email   : yt.chen@bshier.com
@license: Apache Licence
@software: PyCharm
@file    : helper.py
@time    : 2018/9/11 19:44
"""
import json
import logging
import time

import gevent
import six
from tddc.base.util import Singleton

from ...base.redisex_for_manager import RedisExForManager

log = logging.getLogger(__name__)


@six.add_metaclass(Singleton)
class AuthManager(object):

    apply_key = 'tddc:worker:register:apply'

    white_key = 'tddc:worker:register:white'

    black_key = 'tddc:worker:register:black'

    pass_key_fmt = 'tddc:worker:register:pass:{}:{}:{}'

    def __init__(self):
        super(AuthManager, self).__init__()
        gevent.spawn(self.run)
        gevent.sleep()

    def run(self):
        while True:
            register = RedisExForManager().brpop('tddc:worker:register')[1]
            if not register:
                gevent.sleep(10)
                continue
            try:
                register_dict = json.loads(register)
                mac = register_dict.get('s_mac')
                if RedisExForManager().keys(self.white_key + ':{}'.format(mac)):
                    RedisExForManager().lpush(
                        self.pass_key_fmt.format(
                            register_dict.get('s_ip'),
                            register_dict.get('s_platform'),
                            register_dict.get('i_pid')
                        ),
                        json.dumps({'code': 0, 'msg': 'Auth Success.'})
                    )
                elif RedisExForManager().keys(self.black_key + ':{}'.format(mac)):
                    RedisExForManager().lpush(
                        self.pass_key_fmt.format(
                            register_dict.get('s_ip'),
                            register_dict.get('s_platform'),
                            register_dict.get('i_pid')
                        ),
                        json.dumps({'code': -1000, 'msg': 'Reject.'})
                    )
                else:
                    RedisExForManager().hmset(
                        self.apply_key + ':{}'.format(mac), register_dict
                    )
            except Exception as e:
                log.exception(e)

    def get_registration_list(self):
        keys = RedisExForManager().keys(self.apply_key + ':*')
        return [RedisExForManager().hgetall(key) for key in keys]

    def get_white_list(self):
        keys = RedisExForManager().keys(self.white_key + ':*')
        return [RedisExForManager().hgetall(key) for key in keys]

    def edit_white_list(self, worker):
        RedisExForManager().hmset(
            self.white_key + ':{}'.format(
                worker.get('s_mac')
            ),
            {
                's_name': worker.get('s_name', ''),
                's_desc': worker.get('s_desc', '')
            }
        )

    def remove_from_white_list(self, worker):
        RedisExForManager().delete(
            self.white_key + ':{}'.format(
                worker.get('s_mac')
            )
        )

    def get_black_list(self):
        keys = RedisExForManager().keys(self.black_key + ':*')
        return [RedisExForManager().hgetall(key) for key in keys]

    def edit_black_list(self, worker):
        RedisExForManager().hmset(
            self.black_key + ':{}'.format(
                worker.get('s_mac')
            ),
            {
                's_name': worker.get('s_name', ''),
                's_desc': worker.get('s_desc', '')
            }
        )

    def remove_from_black_list(self, worker):
        RedisExForManager().delete(
            self.black_key + ':{}'.format(
                worker.get('s_mac')
            )
        )

    def auth(self, is_pass, worker):
        RedisExForManager().delete(
            self.apply_key + ':{}'.format(worker.get('s_mac'))
        )
        if not worker.get('s_mac'):
            return
        RedisExForManager().sadd(
            self.white_key if is_pass else self.black_key,
            json.dumps({
                's_ip': worker.get('s_ip'),
                's_mac': worker.get('s_mac')
            })
        )
        RedisExForManager().hmset(
            (self.white_key if is_pass else self.black_key) + ':{}'.format(
                worker.get('s_mac')
            ),
            {
                's_name': worker.get('s_name', ''),
                's_ip': worker.get('s_ip'),
                's_mac': worker.get('s_mac'),
                's_desc': worker.get('s_desc', ''),
                'i_date': str(int(time.time()))
            }
        )
        RedisExForManager().lpush(
            self.pass_key_fmt.format(
                worker.get('s_ip'), worker.get('s_platform'), worker.get('i_pid')
            ),
            json.dumps({
                'code': 0 if is_pass else -1000,
                'msg': 'Pass' if is_pass else 'Reject.'
            })
        )
