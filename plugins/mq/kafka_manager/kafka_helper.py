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
                             consumer_timeout_ms=5000,
                             max_poll_records=32,
                             api_version=(0, 10, 1))

    @classmethod
    def make_producer(cls, bootstrap_servers=None):
        global BOOTSTRAP_SERVERS
        if bootstrap_servers:
            BOOTSTRAP_SERVERS = bootstrap_servers
        return KafkaProducer(bootstrap_servers=BOOTSTRAP_SERVERS,
                             api_version=(0, 10, 1))


import random
partitions = {'=>': set(), '==>': set(), '===>': set()}
values = [i for i in range(666)]
cnts = {'=>': 0, '==>': 0}
g = 'test_group%d' % int(random.randrange(1,9999999))

def c(tag):
    import Queue
    global partitions, values, cnts, g
    q = Queue.Queue()
    c = KafkaHelper.make_consumer(topic='test_topic',
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
                time.sleep(0.3)
                continue
            c.subscribe('test_topic')
            partitions = {'=>': set(), '==>': set(), '===>': set()}
            print('resume')
        records = c.poll(2000, 16)
        if not len(records):
            time.sleep(1)
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
    threading.Thread(target=c, args=('=>',)).start()
    threading.Thread(target=c, args=('==>',)).start()
    
    p = KafkaHelper.make_producer()
    cnt = 0
    while cnt < 666:
        p.partitions_for('test_topic')
        p.send('test_topic', str(cnt))
        time.sleep(0.1)
        cnt += 1
    print('Done')

if __name__ == '__main__':
    import time
    import threading
    import logging
    logging.basicConfig(level=logging.WARNING)
    main()
