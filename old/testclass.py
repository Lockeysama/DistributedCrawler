# -*- coding:utf-8 -*-
from tddc import Singleton


class A(object):
    __metaclass__ = Singleton

    def __init__(self):
        print('xxxxxxxxxxxxxxxxxxxxxxx')
