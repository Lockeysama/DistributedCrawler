# -*- coding: utf-8 -*-
'''
Created on 2017年9月6日

@author: chenyitao
'''

from setuptools import setup, find_packages

setup(
    name='tddc',
    version='4.0',
    packages=find_packages(),
    install_requires=[
        'gevent',
        'pymongo',
        'requests',
        'pymysql',
        'mysqlclient',
        'redis-py-cluster',
        'netifaces',
        'psutil',
        'setproctitle',
        'pytz'
    ]
)
