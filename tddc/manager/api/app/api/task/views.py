# encoding: utf-8
"""
@version: ??
@author: chenyitao
@license: Apache Licence 
@software: PyCharm
@file: views.py
@time: 2019-02-04 21:20
"""
import logging
import sys
from collections import defaultdict

from flask import jsonify, request
from tddc.worker import KeepTask, TimingTask

from ...base.define import DATA_EMPTY
from ...base.redisex_for_manager import RedisExForManager
from ...auth.models import login_required
from .. import api

from .helper import TaskHelper, TaskPadHelper

log = logging.getLogger(__name__)


@api.route('/task/list')
@login_required
def timing_task_list():
    keys = RedisExForManager().keys('tddc:task:config:timing:*')
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


@api.route('/task/detail')
@login_required
def timing_task_detail():
    feature = request.args.get('feature')
    data = RedisExForManager().hgetall('tddc:task:config:timing:{}'.format(feature))
    if not data:
        return jsonify({
            'code': DATA_EMPTY,
            'message': 'No Data'}
        )
    return jsonify({'code': 0, 'message': 'success', 'data': data})


@api.route('/task/edit', methods=["POST"])
@login_required
def timing_task_edit():
    task = request.json
    if task.get('s_id') == '-1':
        if sys.version > '3':
            task.pop('s_id')
        else:
            del task['s_id']
    task = TimingTask(**task)
    TaskHelper().edit(task)
    return jsonify({
        'code': 0,
        'message': 'success',
        'data': {'feature': task.s_feature}}
    )


@api.route('/task/delete')
@login_required
def delete_timing_task():
    feature = request.args.get('feature')
    TaskHelper().delete(feature)
    return jsonify({
        'code': 0,
        'message': 'success',
        'data': {'feature': feature}}
    )


@api.route('/keep_task/list')
@login_required
def keep_task_list():
    keys = RedisExForManager().keys('tddc:task:config:keep:*')
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


@api.route('/keep_task/detail')
@login_required
def keep_task_detail():
    platform = request.args.get('platform')
    market = request.args.get('market')
    keys = RedisExForManager().keys('tddc:task:config:keep:{}:{}*'.format(platform, market))
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


@api.route('/task_pad/edit', methods=["POST"])
@login_required
def keep_task_edit():
    task = request.json
    task = KeepTask(**task)
    TaskPadHelper().edit(task)
    return jsonify({
        'code': 0,
        'message': 'success',
        'data': {'feature': task.s_feature}}
    )


@api.route('/task_pad/delete')
@login_required
def delete_keep_task():
    platform = request.args.get('platform')
    feature = request.args.get('feature')
    TaskPadHelper().delete(platform, feature)
    return jsonify({
        'code': 0,
        'message': 'success',
        'data': {'feature': feature}}
    )


@api.route('/task_pad/start_ws_task', methods=['POST'])
@login_required
def start_ws_task():
    platform = request.json.get('platform')
    feature = request.json.get('feature')
    task_pad_task = TaskPadHelper().query(platform, feature)
    TaskPadHelper().start_task(task_pad_task)
    return jsonify({
        'code': 0,
        'message': 'success',
        'data': {'feature': feature}}
    )


@api.route('/task_pad/stop_ws_task', methods=['POST'])
@login_required
def stop_ws_task():
    platform = request.json.get('platform')
    feature = request.json.get('feature')
    task_pad_task = TaskPadHelper().query(platform, feature)
    TaskPadHelper().stop_task(task_pad_task)
    return jsonify({
        'code': 0,
        'message': 'success',
        'data': {'feature': feature}}
    )
