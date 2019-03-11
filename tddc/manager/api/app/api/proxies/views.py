# encoding: utf-8
"""
@version: ??
@author: chenyitao
@license: Apache Licence 
@software: PyCharm
@file: views.py
@time: 2019-02-07 15:05
"""
import logging
from collections import defaultdict

from flask import jsonify, request

from ...base.define import DATA_EMPTY
from ......worker.redisex import RedisEx
from ...auth.models import login_required
from .. import api

from .helper import ProxyHelper
from .models import ProxyTask

log = logging.getLogger(__name__)


@api.route('/proxies/list')
@login_required
def proxies_list():
    keys = RedisEx().keys('tddc:worker:config:common:proxy_check_list:*')
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


@api.route('/proxies/detail')
@login_required
def proxies_detail():
    feature = request.args.get('feature')
    data = RedisEx().hgetall('tddc:worker:config:common:proxy_check_list:{}'.format(feature))
    if not data:
        return jsonify({
            'code': DATA_EMPTY,
            'message': 'No Data'}
        )
    return jsonify({'code': 0, 'message': 'success', 'data': data})


@api.route('/proxies/edit', methods=["POST"])
@login_required
def proxies_edit():
    task = request.json
    task = ProxyTask(**task)
    ProxyHelper().edit(task)
    return jsonify({
        'code': 0,
        'message': 'success',
        'data': {'feature': task.s_feature}}
    )


@api.route('/proxies/delete')
@login_required
def delete_proxies():
    feature = request.args.get('feature')
    ProxyHelper().delete(feature)
    return jsonify({
        'code': 0,
        'message': 'success',
        'data': {'feature': feature}}
    )
