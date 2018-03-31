# -*- coding: utf-8 -*-
'''
Created on 2017年6月12日

@author: chenyitao
'''

import json
import logging
import gevent

from .models import DBSession, WorkerModel
from .extern_modules.extern_manager import ExternManager
from .status import StatusManager
from .event import EventCenter
from .storager import Storager

log = logging.getLogger(__name__)


class WorkerManager(object):
    '''
    Worker管理
    '''

    def __init__(self):
        super(WorkerManager, self).__init__()
        self.worker = DBSession.query(WorkerModel).get(1)
        ExternManager()
        gevent.spawn(self._feedback_plugin_status)
        gevent.sleep()
        StatusManager().sadd('tddc:client:alive', '%s|%s' % (self.worker.name, self.worker.feature))

    def _feedback_plugin_status(self):
        """
        将个服务模块状态写入Redis
        """
        while True:
            gevent.sleep(15)
            try:
                self._feedback()
            except Exception as e:
                log.exception(e)
                log.error('Feedback Status Exception.')

    def _feedback(self):
        status = {'Redis': EventCenter().get_connection_status().alive_timestamp,
                  'HBase': Storager().hbase_status.alive_timestamp,
                  'Mongo': Storager().mongo_status.alive_timestamp}
        StatusManager().set_status('tddc:status:client',
                                   '%s|%s' % (self.worker.name, self.worker.feature),
                                   json.dumps(status))

    @staticmethod
    def start():
        pass
