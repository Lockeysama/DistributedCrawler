# -*- coding: utf-8 -*-
'''
Created on 2017年5月5日

@author: chenyitao
'''

import gevent

from old import ExceptionSite
from old import PublicQueues
from old import TDDCLogging
from old import singleton
from ..plugins import KafkaHelper


@singleton
class ExceptionCollection(object):
    '''
    classdocs
    '''

    def start(self, nodes):
        self._nodes = nodes
        TDDCLogging.info('-->Exception Manager Is Starting.')
        self._exception_producer = KafkaHelper.make_producer(self._nodes)
        gevent.spawn(self._send)
        gevent.sleep()
        TDDCLogging.info('-->Exception Manager Was Ready.')

    def _send(self):
        while True:
            exception = PublicQueues.EXCEPTION.get()
            self._exception_producer.send(ExceptionSite.EXCEPTION_TOPIC,
                                          exception.to_json())
            
            
def main():
    pass

if __name__ == '__main__':
    main()
