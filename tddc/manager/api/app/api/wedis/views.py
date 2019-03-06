# encoding: utf-8
"""
@version: ??
@author: chenyitao
@license: Apache Licence 
@software: PyCharm
@file: views.py
@time: 2019-02-03 16:26
"""
import logging
import time
import zlib
from collections import defaultdict

from flask import jsonify, request

from ...base.define import CMD_INVALIDATE
from ...base.redisex_for_manager import RedisExForManager
from ...auth.models import login_required
from .. import api

log = logging.getLogger(__name__)


def _next_path_query(keys, prefix):
    layer = len(prefix.split(':')) - 1
    count = defaultdict(int)
    next_layer_path = set()
    for key in set(keys):
        full_path = key.split(':')
        if len(full_path) > layer + 1 and key.find(prefix) >= 0:
            path = full_path[layer + 1]
            if path != full_path[-1]:
                count[path] += 1
            next_layer_path.add(path)
    results = []
    for index, path in enumerate(next_layer_path):
        item = {
            'node': path,
            'id': layer * 10000000 + index,
            'path': '{}:{}'.format(prefix, path),
            'leaf': True
        }
        if count.get(path, 0):
            item['count'] = count.get(path)
            item['leaf'] = False
        results.append(item)
    return results


@api.route('/redis/next_path_query')
@login_required
def next_path_query():
    prefix = request.args.get('prefix')
    keys = RedisExForManager().keys('{}:*'.format(prefix))
    return jsonify(_next_path_query(keys, prefix))


@api.route('/redis/query')
@login_required
def get_key_content():
    key = request.args.get('key')
    redis_methods = {'hash': RedisExForManager().hgetall,
                     'set': RedisExForManager().smembers,
                     'list': RedisExForManager().lrange,
                     'string': RedisExForManager().get}
    key_type = RedisExForManager().type(key)
    method = redis_methods.get(key_type)
    if not method:
        return jsonify({
            'code': CMD_INVALIDATE,
            'message': '"CMD({})" Invalidate'.format(key)}
        )
    result = dict()
    result['cmd'] = '{} {}'.format(method.__name__, key)
    result['date'] = time.ctime()
    if key_type == 'list':
        data = method(key, 0, 100)
        result['result'] = data
        length = RedisExForManager().llen(key)
        result['len'] = length
    elif key_type == 'string':
        data = {'value': method(key).encode('utf')}
        result['result'] = data
    elif key_type == 'set':
        data = method(key)
        result['result'] = list(data)
        result['len'] = len(data)
    else:
        if ':cache:' in key:
            data = u'数据过大，请使用 HGET 单独获取数据'
        else:
            data = method(key)
        result['result'] = data
    return jsonify(result)


@api.route('/redis/set')
@login_required
def set_key_content():
    cmd = request.args.get('cmd')
    if not cmd:
        return jsonify({'error': u'请输入命令', 'date': time.ctime()})
    cmd = cmd.split(' ')
    if cmd[0] == 'clean':
        ret = RedisExForManager().clean(cmd[1])
        return jsonify({'result': ret, 'date': time.ctime(), 'cmd': ' '.join(cmd)})
    elif cmd[0].lower() in ('subscribe',):
        return jsonify({'result': u'该命令被禁用', 'cmd': ' '.join(cmd), 'date': time.ctime()})
    else:
        result = dict()
        result['cmd'] = ' '.join(cmd)
        result['date'] = time.ctime()
        try:
            ret = RedisExForManager().execute_command(*cmd)
            if cmd[0] == 'hget' and ':cache:' in cmd[1]:
                ret = zlib.decompress(ret)
            result['result'] = ret
            if isinstance(ret, set) or isinstance(ret, list):
                result['len'] = len(ret)
        except Exception as e:
            result['result'] = e.args[0]
        return jsonify(result)
