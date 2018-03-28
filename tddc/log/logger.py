# -*- coding: utf-8 -*-
'''
Created on 2017年4月10日

@author: chenyitao
'''

import logging
import sys


sys.stderr = sys.stdout
logging.CRITICAL = 35
logging.FATAL = logging.CRITICAL
logging.ERROR = 35
logging.WARNING = 33
logging.WARN = logging.WARNING
logging.INFO = 32
logging.DEBUG = 31
logging.NOTSET = 0

logging._levelNames = {
    logging.CRITICAL: 'CRITICAL',
    logging.ERROR: 'ERROR',
    logging.WARNING: 'WARNING',
    logging.INFO: 'INFO',
    logging.DEBUG: 'DEBUG',
    logging.NOTSET: 'NOTSET',
    'CRITICAL': logging.CRITICAL,
    'ERROR': logging.ERROR,
    'WARN': logging.WARNING,
    'WARNING': logging.WARNING,
    'INFO': logging.INFO,
    'DEBUG': logging.DEBUG,
    'NOTSET': logging.NOTSET,
}

logging.basicConfig(filemode='a',
                    filename='processing.log',
                    format=('[%(asctime)s] [%(levelname)s] '
                            '[%(name)s:%(lineno)s:%(funcName)s] '
                            ' )=> %(message)s'),
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.DEBUG)

stream = logging.StreamHandler()
stream.setLevel(logging.NOTSET)
stream.setFormatter(logging.Formatter(fmt=('\33[1m\33[%(levelno)dm[%(asctime)s] [%(levelname)s] '
                                           '[%(name)s:%(lineno)s:%(funcName)s] '
                                           ' )=> %(message)s\33[0m'),
                                      datefmt='%Y-%m-%d %H:%M:%S'))
logging.getLogger().addHandler(stream)
