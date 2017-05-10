# -*- coding: utf-8 -*-
'''
Created on 2017年5月10日

@author: chenyitao
'''

from plugins import KafkaHelper
from conf.base_site import KAFKA_HOST_PORT


class MQBase(object):
    '''
    classdocs
    '''

    def __init__(self, group=None):
        '''
        Constructor
        '''
        self._consumer = KafkaHelper.make_consumer(group, KAFKA_HOST_PORT)
        self._producer = KafkaHelper.make_producer(KAFKA_HOST_PORT)
    
    def consuemr(self):
        return self._consumer
    
    def subscribe(self, topics, pattern=None, listener=None):
        self._consumer.subscribe(topics, pattern, listener)
    
    def unsubscribe(self):
        self._consumer.unsubscribe()
    
    def producer(self):
        return self._producer 

        
def main():
    pass

if __name__ == '__main__':
    main()
