# encoding: utf-8
"""
@version: ??
@author: chenyitao
@license: Apache Licence 
@software: PyCharm
@file: demo.py
@time: 2019-03-25 11:04
"""
import sqlite3
from multiprocessing import Manager
from os import getpid

import gevent.queue
import pandas as pd

d = Manager().dict()


def p1():
    while True:
        d['data'] = pd.DataFrame([{'S': 1}])
        print('p1', getpid())
        gevent.sleep(1)


def p2():
    gevent.sleep(2)
    while True:
        data = d.get('data')
        print(data)
        print('p2', getpid())
        gevent.sleep(1)


if __name__ == '__main__':
    pid = gevent.fork()
    if pid:
        p1()
    else:
        p2()
    while True:
        gevent.sleep(10)
        print('main', getpid())
