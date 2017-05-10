# -*- coding: utf-8 -*-
'''
Created on 2017年5月2日

@author: chenyitao
'''
from kafka import KafkaConsumer
from kafka.producer.kafka import KafkaProducer


class KafkaHelper(object):
    '''
    classdocs
    '''

    @classmethod
    def make_consumer(cls, bootstrap_servers=None, topic=None, group=None, enable_auto_commit=True):
        if not bootstrap_servers:
            bootstrap_servers = 'localhost:9092'
        return KafkaConsumer(topic,
                             bootstrap_servers=bootstrap_servers,
                             group_id=group,
                             enable_auto_commit=enable_auto_commit,
                             heartbeat_interval_ms=9000,
                             consumer_timeout_ms=5000,
                             max_poll_records=32,
                             api_version=(0, 10, 1))

    @classmethod
    def make_producer(cls, bootstrap_servers=None):
        if not bootstrap_servers:
            bootstrap_servers = 'localhost:9090'
        return KafkaProducer(bootstrap_servers=bootstrap_servers,
                             api_version=(0, 10, 1))


import random
partitions = {'=>': set(), '==>': set(), '===>': set()}
values = [i for i in range(666)]
cnts = {'=>': 0, '==>': 0}
g = 'test_group%d' % int(random.randrange(1,9999999))

KAFKA_HOST_PORT = '72.127.2.48:9092'

def c(tag):
    import Queue
    global partitions, values, cnts, g, KAFKA_HOST_PORT
    q = Queue.Queue()
    c = KafkaHelper.make_consumer(KAFKA_HOST_PORT,
                                  topic='test_topic',
                                  group=g,
                                  enable_auto_commit=True)
    while True:
        while q.qsize() > 32 and tag == '=>':
            c.commit()
            c.unsubscribe()
            partitions = {'=>': set(), '==>': set(), '===>': set()}
            print('pause')
            while not q.empty():
                q.get()
                gevent.sleep(0.3)
                continue
            c.subscribe('test_topic')
            partitions = {'=>': set(), '==>': set(), '===>': set()}
            print('resume')
        records = c.poll(2000, 16)
        if not len(records):
            gevent.sleep(1)
            continue
        for _,record in records.items():
            for msg in record:
                try:
                    values.remove(int(msg.value))
                except Exception, e:
                    print(e)
                partitions[tag].add(msg.partition)
                cnts[tag] += 1
                print(tag, msg.partition, msg.value, partitions[tag], cnts[tag])
                q.put(msg)


                    
def main():    
#     threading.Thread(target=c, args=('=>',)).start()
#     threading.Thread(target=c, args=('==>',)).start()
    import gevent.monkey
    gevent.monkey.patch_all()
    
    gevent.spawn(c, '=>')
    gevent.sleep()
    gevent.spawn(c, '==>')
    gevent.sleep()
    
    p = KafkaHelper.make_producer(KAFKA_HOST_PORT)
    
    cnt = 0
    while cnt < 666:
        p.partitions_for('test_topic')
        p.send('test_topic', str(cnt))
        gevent.sleep(0.1)
        cnt += 1
    print('Done')

if __name__ == '__main__':
    import time
    import threading
    import logging
    
    logging.basicConfig(level=logging.WARNING)
    main()
