# -*- coding:utf-8 -*-
import hashlib
import re

import gevent

# from tddc import ConfigCenter, Singleton, WorkerConfigCenter
# # from tddc import EventCenter
# from tddc import ExternManager
# from tddc.worker.event import EventCenter
# from tddc.worker.message_queue import MessageQueue
import time


def _callback(*args, **kwargs):
    print(args, kwargs)


def juz():
    for i in range(10):
        s = ''
        for j in range(10):
            s += '[%d:%d]  ' % (i, j)
        print(s)
        print('\n')


def map_test():
    def _test(c, a):
        return a + 1
    # _test(c=1, b=2)
    import gevent.pool
    g = gevent.pool.Group()
    print(g.map(_test, [(1, 2), 2]))


def cerely_test():
    import time
    from tddc.celery.tasks import add
    result = add.delay(3, 4)
    while not result.ready():
        time.sleep(1)
    print(result.get())


def type_test():
    class Task(object):
        class Status(object):
            CrawlTopic = 0

            WaitCrawl = 1
            CrawledSuccess = 200
            # CrawledFailed : 错误码为HTTP Response Status

            WaitParse = 1001
            ParseModuleNotFound = 1100
            ParsedSuccess = 1200
            ParsedFailed = 1400

        id = None

        platform = None

        feature = None

        url = None

        method = None

        proxy = None

        space = None

        headers = None

        status = None

        timestamp = None

        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                self.__dict__[k] = v
            # from tddc import ShortUUID
            self.id = kwargs.get('id', 'xxxxxxxxxx')
            self.timestamp = kwargs.get('timestamp', int(time.time()))

        def to_dict(self):
            print(self.__dict__)

    a = Task(**{})
    a.to_dict()
    print(a)


def main():
    type_test()
    # cerely_test()
    # map_test()
    # juz()
    # req()
    # mq()
    # worker()
    # event()
    # hbase()
    # kafka()
    # redis()
    # config()
    # extern_manager()
    while True:
        gevent.sleep(10)
    print(1)


def req():
    from PIL import Image
    import pytesseract
    pytesseract.pytesseract.tesseract_cmd = '/usr/local/bin/tesseract'
    path = '/Users/chenyitao/git/tuodao/tddc_tools/tools/captcha_identity/captchas/hello1/other/'
    name = '2b9q_2.jpg'
    print(pytesseract.image_to_string(Image.open(path + name)))

    import requests
    x = requests.get('https://www.che300.com/pinggu/v12c12m19571r2008-1g1?click=homepage&rt=1516269251291',
                     headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36'},
                     proxies={'http': 'http://1.194.162.229:52460'})
    timestamp = re.search('window.location.href,t="(.*?)",', x.content).groups()[0]
    spidercooskie, spidercode = re.findall('document.cookie="(.*?)="', x.content)
    _m = hashlib.md5()
    _m.update(timestamp)
    code = _m.hexdigest()
    code = code[16:] + code[:16]
    set_cookie = [cookie for cookie in self.response.headers.getlist('Set-Cookie')
                  if '_che300' in cookie][-1].split(';')[0].split('=')[1]
    task.cookies = {spidercooskie: timestamp,
                    spidercode: code,
                    '_che300': set_cookie}

    print(x)


def mq():
    task = WorkerConfigCenter().get_task()
    mq = MessageQueue()
    while True:
        ret = mq.pull(task.consumer_topic, 3)
        print(ret)
        if not ret:
            gevent.sleep(2)


def worker():
    WorkerConfigCenter()


def event():
    EventCenter()
    pass
    # while True:
    #     gevent.sleep(100)


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
    node = type('Node', (), {})
    node.host = '72.127.2.48'
    node.port = 9090
    h = HBaseManager([node])
    x = h.get_async(_callback, 'qwert', 'qwert', 'content')
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
    StatusManager().set_the_hash_value_for_the_hash('test:event:status:test',
                                                    'test_id_10',
                                                    'test:event:status:value:test_id_10',
                                                    'client1',
                                                    '1000')
    StatusManager().set_the_hash_value_for_the_hash('test:event:status:test',
                                                    'test_id_10',
                                                    'test:event:status:value:test_id_10',
                                                    'client1',
                                                    '1200')
    StatusManager().set_the_hash_value_for_the_hash('test:event:status:test',
                                                    'test_id_10',
                                                    'test:event:status:value:test_id_10',
                                                    'tddc_worker_monitor_host_id',
                                                    '1200')
    print(StatusManager().get_the_hash_value_for_the_hash('test:event:status:test', 'test_id_10', 'client2'))
    print(StatusManager().get_the_hash_value_for_the_hash('test:event:status:test', 'test_id_10'))
    print(RecordManager().get_record_sync('tddc.event.record.crawler.a',
                                          '1-1505811162.56-1799',
                                          _callback))
    RecordManager().logger.debug('Record')
    CacheManager()
    print(CacheManager().get_random('tddc:proxy:pool:che300'))
    CacheManager().logger.info('Cache')
    StatusManager()
    print(StatusManager().get_status('tddc.task.status.che300.1200',
                                     'XRTDepEFx255UPyqEZEJsG'))
    StatusManager().logger.error('Status')


if __name__ == '__main__':
    try:
        main()
        while True:
            gevent.sleep(10)
    except Exception as e:
        print(e)
    print('End.')
