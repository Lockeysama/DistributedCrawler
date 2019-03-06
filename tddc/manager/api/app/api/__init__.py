# encoding: utf-8
"""
@version: ??
@author: chenyitao
@license: Apache Licence 
@software: PyCharm
@file: __init__.py.py
@time: 2018/3/19 09:59
"""

from flask import Blueprint

api = Blueprint('api', __name__)

from . import wedis
from . import task
from . import modules
from . import configuration
from . import proxies
from . import workers
