# -*- coding: utf-8 -*-
'''
Created on 2017年4月10日

@author: chenyitao
'''

import time

class Consumer(object):
    '''
    classdocs
    '''

    def __init__(self, kafka_client, topic, zk, group='py_crawler_consumer', auto_commit=True):
        '''
        Constructor
        '''
        self._pause = False
        self._client = kafka_client
        self._topic = self._client.topics[topic]
        self._balanced_consumer = self._topic.get_balanced_consumer(consumer_group=group,
                                                                    zookeeper_connect=zk,
                                                                    auto_commit_enable=auto_commit)
    
    def start(self):
        for msg in self._balanced_consumer:
            yield msg
            if self._pause:
                break
        print('Consumer Paused.')
        
    def stop(self):
        self._pause = True
        self._balanced_consumer
    
    def pause(self):
        self._balanced_consumer.pause()
        
    def resume(self):
        self._balanced_consumer.resume()
         
    
def main():
    import threading
    from pykafka import KafkaClient
    
    def consumer_thread(consumer):
        print('starting...')
        msgs = consumer.start()
        for msg in msgs:
            print(msg)
    
    client = KafkaClient(hosts='72.127.2.48:9092')
    consumer = Consumer(client, 'p_test', '72.127.2.48:2181', )
    c = threading.Thread(target=consumer_thread, name='consumer', args=(consumer,))
    c.start()
#     c.join()
    
    cnt = 60
    while cnt > 0:
        cnt -= 1
        if cnt == 5:
            print('pause...')
            consumer.pause()
        time.sleep(1)
    
    print('done')
        
if __name__ == '__main__':
    main()
    