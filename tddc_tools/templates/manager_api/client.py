# encoding: utf-8
"""
@version: ??
@author: chenyitao
@license: Apache Licence 
@software: PyCharm
@file: client.py
@time: 2018/3/20 17:54
"""
import logging
import setproctitle
import sys

from flask_script import Manager
from gevent.monkey import patch_all
from gevent.pywsgi import WSGIServer
from tddc.default_config import default_config
from tddc.worker import EventCenter
from werkzeug.contrib.fixers import ProxyFix

from tddc_manager_api.app.api.workers.helper import AuthManager
from tddc_manager_api.app import create_app

app = create_app()

app.wsgi_app = ProxyFix(app.wsgi_app)
manager = Manager(app)

log = logging.getLogger(__name__)


def start_plugin():
    import tddc.worker.monitor
    from tddc_manager_api.app.base.redisex_for_manager import RedisExForManager
    tddc.worker.monitor.RedisEx = RedisExForManager
    tddc.worker.monitor.Monitor()
    from tddc_manager_api.app.api.task.helper import TaskHelper, TaskPadHelper
    EventCenter()
    TaskHelper()
    TaskPadHelper()
    AuthManager()


class LocalTest(object):

    def __init__(self):
        setproctitle.setproctitle(default_config.PLATFORM)
        patch_all()
        start_plugin()
        app.run(port=5001)


if __name__ == '__main__':
    if len(sys.argv) == 1:
        setproctitle.setproctitle('TDDC-{}'.format(default_config.PLATFORM))
        patch_all()
        start_plugin()
        host = '0.0.0.0'
        port = 5001
        http_server = WSGIServer((host, port), app)
        log.info('Server(http://{}:{}) Starting.'.format(host, port))
        http_server.serve_forever()
    else:
        manager.add_command('localtest', LocalTest)
        manager.run()
