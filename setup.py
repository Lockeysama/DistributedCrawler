# -*- coding: utf-8 -*-
"""
Created on 2017年9月6日

@author: chenyitao
"""

from setuptools import setup

setup(
    name='tddc',
    version='4.0',
    packages=['tddc', 'tddc_tools'],
    include_package_data=True,
    install_requires=[
        'gevent',
        'pymongo',
        'requests',
        'mysqlclient',
        'redis-py-cluster',
        'netifaces',
        'psutil',
        'setproctitle',
        'pytz',
        'flask',
        'flask_script',
        'flask_moment',
        'flask_httpauth',
        'lxml',
        'websocket-client==0.48.0'
    ],
    entry_points='''
        [console_scripts]
        tddc=tddc_tools.tddc:tddc
    '''
)
