# -*- coding: utf-8 -*-
'''
Created on 2017年5月9日

@author: chenyitao
'''

import logging
import sys

from settings import WORKER


class TDDCLogger(object):

    def __init__(self):
        _format = '[%(levelname)s] [%(asctime)s] [%(filename)s:%(lineno)s] => %(message)s'
        logging.basicConfig(format=_format,
                            datefmt='%Y-%m-%d %H:%M:%S',
                            level=logging.DEBUG,
                            filename=WORKER.name+'.log')  # @UndefinedVariable
        self._log = logging.getLogger(WORKER.name)  # @UndefinedVariable
        stream = logging.StreamHandler()
        stream.setLevel(logging.DEBUG)
        fm_stream = logging.Formatter(fmt=('\033[%(mytp)s;%(myfc)s;%(mybc)sm[%(levelname)s]'
                                           ' [%(asctime)s] %(mypath)s => %(message)s\033[0m'),
                                      datefmt='%Y-%m-%d %H:%M:%S')
        stream.setFormatter(fm_stream)
        self._log.addHandler(stream)

    @staticmethod
    def _update_kwargs(kwargs, tp, fc, bc, path=''):
        if not 'extra' in kwargs:
            kwargs['extra'] = {}
        kwargs['extra']['mytp'] = tp
        kwargs['extra']['myfc'] = fc
        kwargs['extra']['mybc'] = bc
        kwargs['extra']['mypath'] = path

    def _get_cur_info(self):
        infos = sys._getframe()
        return (infos.f_back.f_back.f_code.co_filename,
#                 infos.f_back.f_back.f_code.co_name,
                infos.f_back.f_back.f_lineno)

    def debug(self, msg, *args, **kwargs):
        self._update_kwargs(kwargs, '0', '31', '')
        self._log.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self._update_kwargs(kwargs, '0', '32', '')
        self._log.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self._update_kwargs(kwargs, '1', '37', '43')
        self._log.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self._update_kwargs(kwargs, '5', '37', '41', '[%s:%d]' % self._get_cur_info())
        self._log.error(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self._update_kwargs(kwargs, '4', '37', '45', '[%s:%d]' % self._get_cur_info())
        self._log.critical(msg, *args, **kwargs)


TDDCLogging = TDDCLogger()


def main():
    TDDCLogger().debug('msg')
    TDDCLogger().info('test')
    TDDCLogger().warning('test')
    TDDCLogger().error('msg')
    TDDCLogger().critical('msg')

if __name__ == '__main__':
    main()
