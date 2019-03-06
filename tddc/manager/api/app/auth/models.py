# encoding: utf-8
"""
@version: ??
@author: chenyitao
@license: Apache Licence 
@software: PyCharm
@file: models.py
@time: 2018/3/28 17:45
"""
import os
from functools import wraps

import flask
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer,
                          SignatureExpired, BadSignature)

from ..base.define import LOGIN_FAILED
from ..base.redisex_for_manager import RedisExForManager


class User(object):

    username = None

    is_authenticated = False

    @classmethod
    def add_user(cls, username, password, role):
        password_hash = generate_password_hash(password)
        RedisExForManager().hmset(
            'tddc:worker:config:manager:user:{}'.format(username),
            {
                'username': username,
                'password_hash': password_hash,
                'role': role
            }
        )

    @classmethod
    def auth(cls, username, password):
        user = RedisExForManager().hgetall(
            'tddc:worker:config:manager:user:{}'.format(username)
        )
        if not user:
            return False
        if not check_password_hash(user.get('password_hash'), password):
            return False
        return True

    @classmethod
    def generate_auth_token(cls, username, password, expiration=86400):
        s = Serializer(os.environ.get('SECRET_KEY') or 'hello', expires_in=expiration)
        password_hash = generate_password_hash(password)
        token = s.dumps({'username': username, 'password_hash': password_hash}).decode()
        RedisExForManager().setex(
            'tddc:worker:config:manager:user:auth:{}'.format(username), expiration, token
        )
        return token

    @classmethod
    def verify_auth_token(cls, token):
        if not token:
            return None
        s = Serializer(os.environ.get('SECRET_KEY') or 'hello')
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None
        except BadSignature:
            return None
        _token = RedisExForManager().get(
            'tddc:worker:config:manager:user:auth:{}'.format(data.get('username'))
        )
        if _token != token:
            return None
        return data.get('username')

    @classmethod
    def destroy_auth_token(cls, token):
        s = Serializer(os.environ.get('SECRET_KEY') or 'hello')
        try:
            data = s.loads(token)
        except SignatureExpired:
            return False
        except BadSignature:
            return False
        RedisExForManager().delete(
            'tddc:worker:config:manager:user:auth:{}'.format(data.get('username'))
        )


current_user = User()


def login_required(func):
    @wraps(func)
    def _login_required(*args, **kwargs):
        token = flask.request.headers.get('Authorization')
        username = User.verify_auth_token(token)
        global current_user
        if not username:
            current_user.username = None
            current_user.is_authenticated = False
            return flask.jsonify({'code': LOGIN_FAILED, 'message': 'Login Failed'})
        current_user.username = username
        current_user.is_authenticated = True
        ret = func(*args, **kwargs)
        return ret
    return _login_required
