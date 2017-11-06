# -*- coding:utf-8 -*-
import gevent

from tddc import ConfigCenter
from tddc import EventCenter
from tddc import ExceptionCollection
from tddc import ExternManager


def _callback(*args, **kwargs):
    print(args, kwargs)


def main():
    exception()
    event()
    hbase()
    kafka()
    redis()
    config()
    extern_manager()
    print(1)


def exception():
    ExceptionCollection()
    gevent.sleep(2)
    ExceptionCollection().push(type('TestException',
                                    (),
                                    {'name': 'textexception',
                                     'exception_type': 2001,
                                     'timestamp': 12312312,
                                     'host': '72.127.2.48',
                                     'client_id': '12312as',
                                     'id': '123rexxxxxxx'}))


def event():
    EventCenter()


def extern_manager():
    ExternManager()


def config():
    class ConfigCenterExtern(ConfigCenter):
        @staticmethod
        def tables():
            return dict(ConfigCenter.tables(),
                        **{'cookies': {'key': 'TEXT'},
                           'proxies': {'key': 'TEXT'},
                           'task': {'consumer_topic': 'TEXT',
                                    'consumer_group': 'TEXT',
                                    'producer_topic': 'TEXT',
                                    'producer_group': 'TEXT',
                                    'status_key_base': 'TEXT',
                                    'record_key_base': 'TEXT',
                                    'local_task_queue_size': 'TEXT'}})

        def get_cookies(self):
            return self._get_info('cookies')

        def get_proxies(self):
            return self._get_info('proxies')

        def get_task(self):
            return self._get_info('task')

    ConfigCenterExtern()
    em = ConfigCenterExtern().get_extern_modules()
    cheok = ConfigCenterExtern().get_extern_modules('cheok')
    sv = ConfigCenterExtern().get_services()
    kafka = ConfigCenterExtern().get_services('kafka')
    worker = ConfigCenterExtern().get_worker()
    event = ConfigCenterExtern().get_event()
    exception = ConfigCenterExtern().get_exception()
    cookies = ConfigCenterExtern().get_cookies()
    proxies = ConfigCenterExtern().get_proxies()
    task = ConfigCenterExtern().get_task()
    print(em)


def hbase():
    from tddc import HBaseManager
    h = HBaseManager()
    x = h.get_async(_callback, 'che300', '66bb02d7f3f6f1f790362982aa424a94', 'source')
    h.put('qwert', 'qwert', {'content': {'data': 'test'}})
    print(x)


def kafka():
    from tddc import KeepAliveProducer
    from tddc import KeepAliveConsumer
    nodes = ','.join(['72.127.2.48:9092'])
    p = KeepAliveProducer(bootstrap_servers=nodes)
    p.push('tddc_parse', 'Test', _callback)
    count = 0
    p.push('tddc_parse', '{"Test":"%d"}' % count, _callback)
    count += 1
    gevent.sleep(0.1)
    KeepAliveConsumer('tddc_parse', 'xxxxxxxxxxxxxx', 100000000000000000, bootstrap_servers=nodes)


def redis():
    from tddc import RecordManager
    from tddc import CacheManager
    from tddc import StatusManager
    RecordManager()
    print RecordManager().get_record('tddc.event.record.crawler',
                                     '1-1505811162.56-1799',
                                     _callback)
    RecordManager().logger.debug('Record')
    CacheManager()
    print CacheManager().get_random('tddc:test:proxy:ip_dst:che300')
    CacheManager().logger.info('Cache')
    StatusManager()
    print StatusManager().get_status('tddc.task.status.che300.1200',
                                     'XRTDepEFx255UPyqEZEJsG')
    StatusManager().logger.error('Status')


if __name__ == '__main__':
    try:
        main()
        while True:
            gevent.sleep(10)
    except Exception, e:
        print(e)
    print('End.')
