# encoding: utf-8
"""
@version: ??
@author: chenyitao
@license: Apache Licence 
@software: PyCharm
@file: authentication.py
@time: 2018/3/19 10:02
"""
import flask
from flask import request
from flask_httpauth import HTTPBasicAuth

from . import auth
from .models import login_required, User
from ..base.define import LOGIN_FAILED, LOGIN_SUCCESS, LOGOUT

basic_auth = HTTPBasicAuth()


@auth.route('/login', methods=['POST'])
def login():
    login_data = request.json
    username = login_data.get('username')
    password = login_data.get('password')
    if User.auth(username, password):
        ret = {
            'code': LOGIN_SUCCESS,
            'message': 'Login Success',
            'data': [{
                'token': User.generate_auth_token(username, password),
                'user': {'username': username}
            }]
        }
        return flask.jsonify(ret)
    return flask.jsonify({'code': LOGIN_FAILED, 'message': 'Login Failed'})


@auth.route('/logout')
@login_required
def logout():
    User.destroy_auth_token(flask.request.headers.get('Authorization'))
    return flask.jsonify({'code': LOGOUT, 'message': 'Logout'})
