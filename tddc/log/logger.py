# -*- coding: utf-8 -*-
'''
Created on 2017年4月10日

@author: chenyitao
'''

import logging


class TDDCLogger(object):
    name = None

    def __init__(self, log_name='Worker', *args, **kwargs):
        super(TDDCLogger, self).__init__()
        self.name = log_name
        logging.basicConfig(format=('[%(levelname)s] [%(asctime)s] '
                                    '[%(filename)s:%(lineno)s:%(funcName)s]'
                                    ' => %(message)s'),
                            datefmt='%Y-%m-%d %H:%M:%S',
                            level=logging.DEBUG,
                            filename=self.name + '.log')
        stream = logging.StreamHandler()
        stream.name = self.name
        stream.setLevel(logging.DEBUG)
        stream.setFormatter(logging.Formatter(fmt=('[%(levelname)s] [%(asctime)s] '
                                                   '[%(filename)s:%(lineno)s:%(funcName)s]'
                                                   ' => %(message)s'),
                                              datefmt='%Y-%m-%d %H:%M:%S'))
        if stream.name in [handler.name for handler in logging.getLogger(self.name).handlers]:
            return
        logging.getLogger(self.name).addHandler(stream)

    @property
    def logger(self):
        logger = logging.getLogger(self.name)
        return logging.LoggerAdapter(logger, {self.name: self})
