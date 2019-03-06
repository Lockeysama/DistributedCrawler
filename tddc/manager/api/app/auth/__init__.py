# encoding: utf-8
"""
@version: ??
@author: chenyitao
@license: Apache Licence 
@software: PyCharm
@file: __init__.py.py
@time: 2018/3/19 09:59
"""

"""
登录授权控制
"""

from flask import Blueprint

auth = Blueprint('auth', __name__)

from . import views
from . import models
