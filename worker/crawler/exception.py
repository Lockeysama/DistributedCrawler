# -*- coding: utf-8 -*-
'''
Created on 2017年5月5日

@author: chenyitao
'''

import gevent

from conf.base_site import EXCEPTION_TOPIC_NAME, KAFKA_HOST_PORT
from common import TDDCLogging
from common.queues import EXCEPTION_QUEUE

from plugins import KafkaHelper


class ExceptionCollection(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        TDDCLogging.info('-->Exception Manager Is Starting.')
        self._exception_producer = KafkaHelper.make_producer(KAFKA_HOST_PORT)
        gevent.spawn(self._send)
        gevent.sleep()
        TDDCLogging.info('-->Exception Manager Was Ready.')

    def _send(self):
        while True:
            exception = EXCEPTION_QUEUE.get()
            self._exception_producer.send(EXCEPTION_TOPIC_NAME,
                                          exception.to_json())
            
            
def main():
    pass

if __name__ == '__main__':
    main()
