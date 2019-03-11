# encoding: utf-8
"""
@version: ??
@author: chenyitao
@license: Apache Licence 
@software: PyCharm
@file: __init__.py.py
@time: 2019-03-05 16:14
"""
import logging
import setproctitle

from gevent.pywsgi import WSGIServer
from werkzeug.contrib.fixers import ProxyFix

from ...default_config import default_config
from ...worker.monitor import Monitor
from ...worker.event import EventCenter

from .app.api.workers.helper import AuthManager
from .app.api.task.helper import TaskHelper, TaskPadHelper

from .app import create_app

log = logging.getLogger(__name__)


def _start_plugin():
    Monitor()
    EventCenter()
    TaskHelper()
    TaskPadHelper()
    AuthManager()


def start():
    setproctitle.setproctitle('TDDC-{}'.format(default_config.PLATFORM))
    app = create_app()
    app.wsgi_app = ProxyFix(app.wsgi_app)
    _start_plugin()
    host = '0.0.0.0'
    port = 5001
    http_server = WSGIServer((host, port), app)
    log.info('Server(http://{}:{}) Starting.'.format(host, port))
    http_server.serve_forever()
