# -*- coding: utf-8 -*-
'''
Created on 2017年4月10日

@author: chenyitao
'''

import logging
import os
import sys
from logging.handlers import TimedRotatingFileHandler

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


if not os.path.exists('./logs'):
    os.mkdir('./logs')


log_fmt = '[%(asctime)s] [%(levelname)s] [%(name)s:%(lineno)s:%(funcName)s] )=> %(message)s'
formatter = logging.Formatter(log_fmt)

debug_file_handler = TimedRotatingFileHandler(
    filename="./logs/debug.log", when="midnight", backupCount=3
)
debug_file_handler.setFormatter(formatter)
debug_file_handler.setLevel(logging.DEBUG)
logging.getLogger().addHandler(debug_file_handler)

info_file_handler = TimedRotatingFileHandler(
    filename="./logs/info.log", when="midnight", backupCount=3
)
info_file_handler.setFormatter(formatter)
info_file_handler.setLevel(logging.INFO)
logging.getLogger().addHandler(info_file_handler)

warning_handler = TimedRotatingFileHandler(
    filename="./logs/warning.log", when="midnight", backupCount=3
)
warning_handler.setFormatter(formatter)
warning_handler.setLevel(logging.WARNING)
logging.getLogger().addHandler(warning_handler)

error_handler = TimedRotatingFileHandler(
    filename="./logs/error.log", when="midnight", backupCount=3
)
error_handler.setFormatter(formatter)
error_handler.setLevel(logging.ERROR)
logging.getLogger().addHandler(error_handler)

stream = logging.StreamHandler()
stream.setLevel(logging.NOTSET)
stream.setFormatter(logging.Formatter(fmt=('\33[1m\33[%(levelno)dm[%(asctime)s] [%(levelname)s] '
                                           '[%(name)s:%(lineno)s:%(funcName)s] '
                                           ' )=> %(message)s\33[0m'),
                                      datefmt='%Y-%m-%d %H:%M:%S'))
logging.getLogger().addHandler(stream)
