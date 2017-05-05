# -*- coding: utf-8 -*-
'''
Created on 2017年5月2日

@author: chenyitao
'''

from kafka import KafkaConsumer
from kafka.producer.kafka import KafkaProducer

from conf.base_site import KAFKA_HOST, KAFKA_PORT

BOOTSTRAP_SERVERS = '%s:%s' % (KAFKA_HOST, KAFKA_PORT)

class KafkaHelper(object):
    '''
    classdocs
    '''

    @classmethod
    def make_consumer(cls, topic, group, bootstrap_servers=None, enable_auto_commit=True):
        global BOOTSTRAP_SERVERS
        if bootstrap_servers:
            BOOTSTRAP_SERVERS = bootstrap_servers
        return KafkaConsumer(topic,
                             bootstrap_servers=BOOTSTRAP_SERVERS,
                             group_id=group,
                             enable_auto_commit=enable_auto_commit,
                             heartbeat_interval_ms=9000,
                             consumer_timeout_ms=2000,
                             max_poll_records=32,
                             api_version=(0, 10, 1))

    @classmethod
    def make_producer(cls, bootstrap_servers=None):
        global BOOTSTRAP_SERVERS
        if bootstrap_servers:
            BOOTSTRAP_SERVERS = bootstrap_servers
        return KafkaProducer(bootstrap_servers=BOOTSTRAP_SERVERS,
                             api_version=(0, 10, 1))


partitions = {'=>': set(), '==>': set(), '===>': set()}   
def main():
    def c(tag):
        global partitions
        c = KafkaHelper.make_consumer(topic='test_topic', group='test_group', enable_auto_commit=False)
        first = True
        while True:
            print('xxxxxxxxx')
            for msg in c:
                if first:
                    if tag == '==>' or tag == '===>':
                        partitions = {'=>': set(), '==>': set(), '===>': set()}
                        first = False
                    if msg.value == '300':
                        assert(1==2)
                partitions[tag].add(msg.partition)
                print(msg.value, tag, partitions[tag])
                break
    
    threading.Thread(target=c, args=('=>',)).start()
    
    p = KafkaHelper.make_producer()
    cnt = 0
    while cnt < 200:
        if cnt == 50:
            threading.Thread(target=c, args=('==>',)).start()
        elif cnt == 100:
            threading.Thread(target=c, args=('===>',)).start()
        p.send('test_topic', str(cnt))
        time.sleep(0.1)
        cnt += 1

if __name__ == '__main__':
    import time
    import threading
    import logging
    logging.basicConfig(level=logging.WARNING)
    main()
