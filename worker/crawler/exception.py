# -*- coding: utf-8 -*-
'''
Created on 2017年5月5日

@author: chenyitao
'''

import gevent

from conf.base_site import STATUS, EXCEPTION_TOPIC_NAME
from common.queues import EXCEPTION_QUEUE

from plugins.mq.kafka_manager.kafka_helper import KafkaHelper


class ExceptionCollection(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        print('-->Exception Manager Is Starting.')
        gevent.spawn(self._send)
        gevent.sleep()
        print('-->Exception Manager Was Ready.')

    def _send(self):
        self._exception_producer = KafkaHelper.make_producer()
        while STATUS:
            exception = EXCEPTION_QUEUE.get()
            self._exception_producer.send(EXCEPTION_TOPIC_NAME,
                                          exception.to_json())
            
            
def main():
    pass

if __name__ == '__main__':
    main()
