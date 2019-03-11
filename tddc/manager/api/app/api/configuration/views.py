# encoding: utf-8
"""
@version: ??
@author: chenyitao
@license: Apache Licence 
@software: PyCharm
@file: views.py
@time: 2019-02-06 16:12
"""

import logging
from collections import defaultdict

from flask import jsonify, request

from ...base.define import DATA_EMPTY, CONFIG_MODIFY_FAILED, CONFIG_DELETE_FAILED
from ......worker.redisex import RedisEx
from ...auth.models import login_required
from .. import api

from .helper import ConfigsHelper

log = logging.getLogger(__name__)


@api.route('/config/list')
@login_required
def config_list():
    keys = RedisEx().keys('tddc:worker:config:*')
    if not keys:
        return jsonify({
            'code': DATA_EMPTY,
            'message': 'No Data'}
        )
    result = defaultdict(lambda: defaultdict(list))
    for key in keys:
        fields = key.split(':')
        if fields[3] == 'common':
            continue
        if fields[5] not in result[fields[3]][fields[4]]:
            result[fields[3]][fields[4]].append(fields[5])
    return jsonify({'code': 0, 'message': 'success', 'data': result})


@api.route('/config/detail')
@login_required
def config_detail():
    platform = request.args.get('platform')
    ip = request.args.get('ip')
    feature = request.args.get('feature')
    keys = RedisEx().keys('tddc:worker:config:{}:{}:{}:*'.format(
        platform, ip, feature)
    )
    if not keys:
        return jsonify({
            'code': DATA_EMPTY,
            'message': 'No Data'}
        )
    result = defaultdict(lambda: defaultdict(object))
    for key in keys:
        fields = key.split(':')
        data = RedisEx().hgetall(key)
        if len(fields) == 8:
            result[fields[6]][fields[7]] = data
        elif len(fields) == 7:
            result[fields[6]]['default'] = data
    return jsonify({'code': 0, 'message': 'success', 'data': result})


@api.route('/config/edit', methods=["POST"])
@login_required
def config_edit():
    data = request.json
    ret = ConfigsHelper().edit(data.get('path'), data.get('data'))
    return jsonify({
        'code': 0 if ret else CONFIG_MODIFY_FAILED,
        'message': 'success' if ret else 'failed'
    })


@api.route('/config/delete', methods=["POST"])
@login_required
def config_delete():
    data = request.json
    ret = ConfigsHelper().delete(data.get('path'), data.get('data'))
    return jsonify({
        'code': 0 if ret else CONFIG_DELETE_FAILED,
        'message': 'success' if ret else 'failed'
    })
