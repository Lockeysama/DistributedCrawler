# -*- coding: utf-8 -*-
'''
Created on 2017年6月12日

@author: chenyitao
'''

import json
import gevent

from .extern_modules.extern_manager import ExternManager
from .status import StatusManager
from .cache import CacheManager
from .record import RecordManager
from .event import EventCenter
from .storager import Storager
from .worker_config import WorkerConfigCenter
from ..log.logger import TDDCLogger


class WorkerManager(TDDCLogger):
    '''
    classdocs
    '''

    def __init__(self):
        super(WorkerManager, self).__init__()
        self.worker = WorkerConfigCenter().get_worker()
        StatusManager()
        CacheManager()
        RecordManager()
        ExternManager()
        gevent.spawn(self._feedback_plugin_status)
        gevent.sleep()
        StatusManager().sadd('tddc:client:alive', '%s_%s' % (self.worker.name, self.worker.id))

    def _feedback_plugin_status(self):
        while True:
            gevent.sleep(15)
            try:
                self._feedback()
            except Exception as e:
                self.exception(e)
                self.error('Feedback Status Exception.')

    def _feedback(self):
        StatusManager().set_status('tddc:status:client',
                                   self.worker.name + self.worker.id,
                                   json.dumps({'Kafka': EventCenter().get_connection_status().alive_timestamp,
                                               'Redis': StatusManager().get_connection_status().alive_timestamp,
                                               'HBase': Storager().get_connection_status().alive_timestamp}))

    @staticmethod
    def start():
        pass
