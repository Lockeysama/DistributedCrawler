# -*- coding: utf-8 -*-
'''
Created on 2017年4月10日

@author: chenyitao
'''

import time
from pykafka import KafkaClient

class Producer(object):
    '''
    classdocs
    '''

    def __init__(self, kafka_client, topic):
        '''
        Constructor
        '''
        self._client=kafka_client
        self._topic = self._client.topics[topic]
        self._producer = self._topic.get_sync_producer()
    
    def push(self, msg):
        self._producer.produce(msg)
    
    def close(self):
        self._producer.close_producter()

    def __del__(self):
        self.close()

def main():
    def producer_thread(producer):
        print('starting...')
        
    client = KafkaClient(hosts='72.127.2.48:9092')
    producer = Producer(client, 'tddc_testtest')
    import threading
    c = threading.Thread(target=producer_thread, name='producer', args=(producer,))
    c.start()
#     c.join()
    
    cnt = 10
    while cnt > 0:
        cnt -= 1
        print(time.clock())
        producer.push('{"Tick": "Tock"} %d' % cnt + 'x'*300)
        print(time.clock())
        if cnt == 5:
            print('pause...')
#             producer.close()
#         time.sleep(1)
    
    print('done')
        
if __name__ == '__main__':
    main()
