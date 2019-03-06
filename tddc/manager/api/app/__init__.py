# encoding: utf-8
"""
@version: ??
@author: chenyitao
@license: Apache Licence 
@software: PyCharm
@file: __init__.py.py
@time: 2018/3/19 09:59
"""
import os

from flask import Flask
from flask_moment import Moment
# from flask_cors import CORS

moment = Moment()


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'hard to guess string'
    app.config['FLASKY_ADMIN'] = os.environ.get('FLASKY_ADMIN')
    app.config['FLASKY_POSTS_PER_PAGE'] = 20
    app.config['FLASKY_FOLLOWERS_PER_PAGE'] = 50
    app.config['FLASKY_COMMENTS_PER_PAGE'] = 30

    from .auth.models import current_user
    app.add_template_global(current_user, 'current_user')
    # CORS(app, supports_credentials=True)
    moment.init_app(app)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')

    return app
