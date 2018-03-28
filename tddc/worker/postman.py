# -*- coding: utf-8 -*-
'''
Created on 2017年5月2日

@author: chenyitao
'''
import logging

from ..util.util import Singleton
from ..kafka.producer import KeepAliveProducer

from .models import DBSession, KafkaModel

log = logging.getLogger(__name__)


class Postman(KeepAliveProducer):
    __metaclass__ = Singleton

    def __init__(self):
        kafka_info = DBSession.query(KafkaModel).all()
        if not kafka_info:
            log.warning('>>> Kafka Nodes Not Found.')
            return
        kafka_nodes = ','.join(['%s:%s' % (info.host, info.port) for info in kafka_info])
        super(Postman, self).__init__(kafka_nodes)
