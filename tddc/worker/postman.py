# -*- coding: utf-8 -*-
'''
Created on 2017年5月2日

@author: chenyitao
'''

from ..util.util import Singleton
from ..kafka.producer import KeepAliveProducer
from ..log.logger import TDDCLogger

from .worker_config import WorkerConfigCenter


class Postman(KeepAliveProducer):
    __metaclass__ = Singleton

    def __init__(self):
        kafka_info = WorkerConfigCenter().get_kafka()
        if not kafka_info:
            TDDCLogger().warning('>>> Kafka Nodes Not Found.')
            return
        kafka_nodes = ','.join(['%s:%s' % (info.host, info.port) for info in kafka_info])
        super(Postman, self).__init__(kafka_nodes)
