# -*- coding: utf-8 -*-
'''
Created on 2017年5月5日

@author: chenyitao
'''

import gevent

from conf import CrawlerSite
from common import TDDCLogging
from common.queues import CrawlerQueues

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
        self._exception_producer = KafkaHelper.make_producer(CrawlerSite.KAFKA_NODES)
        gevent.spawn(self._send)
        gevent.sleep()
        TDDCLogging.info('-->Exception Manager Was Ready.')

    def _send(self):
        while True:
            exception = CrawlerQueues.EXCEPTION.get()
            self._exception_producer.send(CrawlerSite.EXCEPTION_TOPIC,
                                          exception.to_json())
            
            
def main():
    pass

if __name__ == '__main__':
    main()
