# -*- coding: utf-8 -*-
'''
Created on 2017年9月6日

@author: chenyitao
'''

from setuptools import setup, find_packages

setup(
    name='tddc',
    version='3.0',
    packages=find_packages(),
    install_requires=[
        'gevent',
        'happybase',
        'pymongo',
        'requests',
        'mysql-python',
        'pymysql',
        'redis-py-cluster',
        'logging',
        'netifaces',
        'psutil',
        'setproctitle',
        'pytz'
    ]
)
