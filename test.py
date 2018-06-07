# -*- coding:utf-8 -*-
import hashlib
import re

import MySQLdb
import gevent

# from tddc import ConfigCenter, Singleton, WorkerConfigCenter
# # from tddc import EventCenter
# from tddc import ExternManager
# from tddc.worker.event import EventCenter
# from tddc.worker.message_queue import MessageQueue
import time

from websocket import WebSocketApp

from tddc.mysql.mysql_helper import MySQLHelper


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


def spilt_test():
    keys = ['tddc:task:cache:cheok',
            'tddc:task:cache:che300',
            'tddc:task:queue:crawler',
            'tddc:proxy:source',
            'tddc:proxy:pool']

    keyr = {'tddc': {'task': {'cache': {'cheok': None, 'che300': None},
                              'queue': {'crawler': None}},
                     'proxy': {'source': None,
                               'pool': None}}}

    def list_dict(d, l):
        if not len(l):
            return
        first = l[0]
        d[first] = {}
        l = l[1:]
        if len(l) > 0:
            list_dict(d[first], l)

    def merge_dict(d1, d2):
        keys1 = d1.keys()
        keys2 = d2.keys()
        for i in range(len(keys1) if len(keys1) < len(keys2) else len(keys2)):
            if keys1[i] != keys2[i]:
                if isinstance(keys1, list):
                    if keys2[i] in keys1:
                        merge_dict(d1[keys2[i]], d2[keys2[i]])
                        continue
                d1[keys2[i]] = d2[keys2[i]]
                return
            else:
                merge_dict(d1[keys1[i]], d2[keys1[i]])

    def make_nodes(data, nodes):
        for key, value in data.items():
            node = {'text': key,
                    'nodes': []}
            if value:
                make_nodes(value, node['nodes'])
            nodes.append(node)

    all_fields = []
    result = {}
    for index, key in enumerate(keys):
        ks = key.split(':')
        tmp = {}
        list_dict(tmp, ks)
        all_fields.append(tmp)

    for i in range(len(all_fields) - 1):
        d1 = all_fields[0]
        d2 = all_fields[i + 1]
        merge_dict(d1, d2)

    nodes = []
    make_nodes(all_fields[0], nodes)

    result = {}
    tmp = result
    for j, k in enumerate(all_fields[i]):
        _jks = [fields[j] if len(fields) > j else None for fields in all_fields]
        print(_jks)
        for tag in _jks:
            if not tmp.get(tag):
                tmp[tag] = {}
        tmp = tmp[tag]


    print(ks)


def mongo_test():
    from pymongo import MongoClient
    client = MongoClient('192.168.0.103', 27017)
    print(client)


def subprocess_test():
    import gevent.monkey
    import gevent.queue
    gevent.monkey.patch_all()
    import multiprocessing

    def _g1(q):
        while True:
            print(q.get())
            gevent.sleep(1)

    def _p1():
        q = gevent.queue.Queue()
        gevent.spawn(_g1, q)
        gevent.sleep()
        while True:
            # print(1)
            q.put(1)
            gevent.sleep(1)

    multiprocessing.Process(target=_p1).start()
    while True:
        gevent.sleep(10)


def mysql_test():
    aliyun = 'rm-bp1eq3q0ni7376g35no.mysql.rds.aliyuncs.com'
    aws = 'public-1.cluster-cvt1rggskuer.ap-northeast-1.rds.amazonaws.com'
    db = MySQLdb.Connect(host=aliyun,
                         port=3306,
                         user='bishi',
                         passwd='Zheshimima123',
                         db='bishi',
                         charset='utf8',
                         autocommit=True)
    aws_db = MySQLdb.Connect(host=aws,
                             port=3306,
                             user='bishi',
                             passwd='Zheshimima123',
                             db='bishi',
                             charset='utf8',
                             autocommit=True)
    c = db.cursor()
    sql = ('select code, high, open, low, close, volume, date '
           'from bishi_kline_1h where date >= 1527564600 and date < 1527570000 limit 150000;')
    aws_c = aws_db.cursor()
    try:
        print('fetch data.')
        ret = c.execute(sql)
        if ret:
            records = c.fetchall()
            print(len(records))
            times = len(records) / 100 + 1
            sql_base = ('replace into bishi_kline_1h '
                        '(code, high, open, low, close, volume, date) '
                        'values {};')
            print('write data.')
            for index in range(times):
                if index == times - 1:
                    items = records[100 * index:]
                else:
                    items = records[100 * index: 100 * (index + 1)]
                items = [['\'{}\''.format(v) if isinstance(v, unicode) else str(v) for v in item]
                         for item in items]
                v_str_list = [u' ({}) '.format(u','.join(item))
                              for item in items]
                v_str = ', '.join(v_str_list)
                rp_sql = sql_base.format(v_str)
                aws_c.execute(rp_sql)
                print(index)
    except Exception as e:
        print(e)
    aws_c.close()
    c.close()
    aws_db.close()
    db.close()
    print('done.')


def subprocess_test2():
    import subprocess
    import gevent
    import multiprocessing
    from os import getpid
    
    # class A(subprocess.Popen):
    #     def __init__(self):
    #         super(A, self).__init__(multiprocessing.Process)
    #         print(2)
    #
    # A()
    q = multiprocessing.Queue()

    def _g():
        while True:
            print(getpid())
            gevent.sleep(1)

    gevent.spawn(_g)
    gevent.sleep()

    def p(q):
        while True:
            x = q.get()
            print(getpid(), x)

    multiprocessing.Process(target=p, args=(q,)).start()
    multiprocessing.Process(target=p, args=(q,)).start()
    i = 1
    while i:
        # print(1)
        q.put(i)
        i += 1
        gevent.sleep(1)


def try_test():
    while True:
        try:
            print(1)
            a = 1
            a += '1'
        except TypeError as e:
            print(e)
            time.sleep(1)
        except Exception as e:
            print('exit')
            time.sleep(1)
            raise


def ws_test():
    def on_message(ws, message):
        print(message)

    def on_open(ws):
        ws.send('{"req":"market.btcusdt.kline.1min","id":"kline1528184226049"}')

    ws = WebSocketApp(url='ws://cex.plus/ws/huobipro',
                      on_message=on_message, on_open=on_open)
    ws.run_forever(http_proxy_host='127.0.0.1', http_proxy_port=8118)


def main():
    ws_test()
    # try_test()
    # subprocess_test2()
    # mysql_test()
    # subprocess_test()
    # mongo_test()
    # spilt_test()
    # type_test()
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
    pass
    # from PIL import Image
    # import pytesseract
    # pytesseract.pytesseract.tesseract_cmd = '/usr/local/bin/tesseract'
    # path = '/Users/chenyitao/git/tuodao/tddc_tools/tools/captcha_identity/captchas/hello1/other/'
    # name = '2b9q_2.jpg'
    # print(pytesseract.image_to_string(Image.open(path + name)))
    #
    # import requests
    # x = requests.get('https://www.che300.com/pinggu/v12c12m19571r2008-1g1?click=homepage&rt=1516269251291',
    #                  headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36'},
    #                  proxies={'http': 'http://1.194.162.229:52460'})
    # timestamp = re.search('window.location.href,t="(.*?)",', x.content).groups()[0]
    # spidercooskie, spidercode = re.findall('document.cookie="(.*?)="', x.content)
    # _m = hashlib.md5()
    # _m.update(timestamp)
    # code = _m.hexdigest()
    # code = code[16:] + code[:16]
    # set_cookie = [cookie for cookie in self.response.headers.getlist('Set-Cookie')
    #               if '_che300' in cookie][-1].split(';')[0].split('=')[1]
    # task.cookies = {spidercooskie: timestamp,
    #                 spidercode: code,
    #                 '_che300': set_cookie}
    #
    # print(x)


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
