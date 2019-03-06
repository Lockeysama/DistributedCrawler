# encoding: utf-8
"""
@version: ??
@author: chenyitao
@license: Apache Licence 
@software: PyCharm
@file: views.py
@time: 2019-02-05 09:51
"""

import logging
from collections import defaultdict

from flask import jsonify, request

from ...base.define import DATA_EMPTY
from ...base.redisex_for_manager import RedisExForManager
from ...auth.models import login_required
from .. import api

from .helper import ModulesHelper

log = logging.getLogger(__name__)


@api.route('/modules/list')
@login_required
def modules_list():
    platform = request.args.get('platform')
    market = request.args.get('market')
    if not market:
        query = 'tddc:worker:config:common:extra_modules:{}:*'.format(platform)
    else:
        query = 'tddc:worker:config:common:extra_modules:{}:{}:*'.format(platform, market)
    keys = RedisExForManager().keys(query)
    if not keys:
        return jsonify({
            'code': DATA_EMPTY,
            'message': 'No Data'}
        )
    result = defaultdict(lambda: defaultdict(list))
    for key in keys:
        fields = key.split(':')
        result[fields[-1][0].upper()][fields[-1].split('.')[0]].append(fields[-1])
    return jsonify({'code': 0, 'message': 'success', 'data': result})


@api.route('/modules/detail')
@login_required
def modules_detail():
    platform = request.args.get('platform')
    market = request.args.get('market')
    keys = RedisExForManager().keys(
        'tddc:worker:config:common:extra_modules:{}:{}*'.format(platform, market)
    )
    if not keys:
        return jsonify({
            'code': DATA_EMPTY,
            'message': 'No Data'}
        )
    result = {
        'code': 0, 'message': 'success',
        'data': [], 'platform': platform, 'market': market
    }
    for key in keys:
        resp = RedisExForManager().hgetall(key)
        result['data'].append(resp)
    return jsonify(result)


@api.route('/modules/upload', methods=['POST'])
@login_required
def upload_module():
    owner = request.args.get('platform')
    _file = request.files.get('file')
    print(owner, _file.filename)
    ModulesHelper().edit(owner, _file.filename, _file.stream.read())
    return jsonify({
        'code': 0,
        'message': 'success',
        'data': {'owner': owner, 'filename': _file.filename}}
    )


@api.route('/modules/push', methods=['POST'])
@login_required
def push_module():
    owner = request.json.get('owner')
    feature = request.json.get('feature')
    ModulesHelper().push(owner, feature)
    return jsonify({
        'code': 0,
        'message': 'success'
    })
