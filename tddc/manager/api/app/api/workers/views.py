# encoding: utf-8
"""
@version: ??
@author: chenyitao
@license: Apache Licence 
@software: PyCharm
@file: views.py
@time: 2019-02-15 16:09
"""
from flask import jsonify, request

from ...auth.models import login_required

from .. import api

from .helper import AuthManager


@api.route('/workers/registrationlist')
@login_required
def registration_list():
    _list = AuthManager().get_registration_list()
    return jsonify({
        'code': 0,
        'message': 'success',
        'data': _list
    })


@api.route('/workers/whitelist')
@login_required
def white_list():
    _list = AuthManager().get_white_list()
    return jsonify({
        'code': 0,
        'message': 'success',
        'data': _list
    })


@api.route('/workers/blacklist')
@login_required
def black_list():
    _list = AuthManager().get_black_list()
    return jsonify({
        'code': 0,
        'message': 'success',
        'data': _list
    })


@api.route('/workers/whitelist/edit', methods=['POST'])
@login_required
def white_list_edit():
    worker = request.json.get('worker')
    AuthManager().edit_white_list(worker)
    return jsonify({
        'code': 0,
        'message': 'success'
    })


@api.route('/workers/blacklist/edit', methods=['POST'])
@login_required
def black_list_edit():
    worker = request.json.get('worker')
    AuthManager().edit_black_list(worker)
    return jsonify({
        'code': 0,
        'message': 'success'
    })


@api.route('/workers/whitelist/remove', methods=['POST'])
@login_required
def white_list_remove():
    worker = request.json.get('worker')
    AuthManager().remove_from_white_list(worker)
    return jsonify({
        'code': 0,
        'message': 'success'
    })


@api.route('/workers/blacklist/remove', methods=['POST'])
@login_required
def black_list_remove():
    worker = request.json.get('worker')
    AuthManager().remove_from_black_list(worker)
    return jsonify({
        'code': 0,
        'message': 'success'
    })


@api.route('/workers/auth', methods=['POST'])
@login_required
def auth_pass():
    is_pass = request.json.get('isPass')
    worker = request.json.get('worker')
    AuthManager().auth(is_pass, worker)
    return jsonify({
        'code': 0,
        'message': 'success',
    })
