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

logging.basicConfig(format=('[%(asctime)s] [%(levelname)s] '
                            '[%(name)s:%(lineno)s:%(funcName)s] '
                            ' )=> %(message)s'),
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.DEBUG,
                    filename='Worker.log')


class TDDCLogger(object):
    name = None

    def __init__(self, log_name=None, *args, **kwargs):
        super(TDDCLogger, self).__init__()
        self.name = log_name if log_name else str(self.__class__).strip('\'<class >')
        stream = logging.StreamHandler()
        stream.name = self.name
        stream.setLevel(logging.NOTSET)
        stream.setFormatter(logging.Formatter(fmt=('\33[1m\33[%(levelno)dm[%(asctime)s] [%(levelname)s] '
                                                   '[%(name)s:%(lineno)s:%(funcName)s] '
                                                   ' )=> %(message)s\33[0m'),
                                              datefmt='%Y-%m-%d %H:%M:%S'))
        if stream.name in [handler.name for handler in logging.getLogger(self.name).handlers]:
            return
        logger = logging.getLogger(self.name)
        logger.propagate = 0
        logger.addHandler(stream)
        file = logging.FileHandler('Worker.log')
        file.name = self.name
        file.setLevel(logging.NOTSET)
        file.setFormatter(logging.Formatter(fmt=('[%(asctime)s] [%(levelname)s] '
                                                 '[%(name)s:%(lineno)s:%(funcName)s] '
                                                 ' )=> %(message)s'),
                                            datefmt='%Y-%m-%d %H:%M:%S'))
        logger.addHandler(file)

    @property
    def logger(self):
        logger = logging.getLogger(self.name)
        return logging.LoggerAdapter(logger, {self.name: self})

    @property
    def info(self):
        return self.logger.info

    @property
    def debug(self):
        return self.logger.debug

    @property
    def warning(self):
        return self.logger.warning

    @property
    def error(self):
        return self.logger.error

    @property
    def exception(self):
        return self.logger.exception

    @property
    def critical(self):
        return self.logger.critical
