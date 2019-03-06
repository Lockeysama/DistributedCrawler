# -*- coding: utf-8 -*-
"""
@author  : chenyitao
@email   : yt.chen@bshier.com
@license: Apache Licence
@software: PyCharm
@file    : __init__.py.py
@time    : 2018/10/23 14:49
"""
from gevent.monkey import patch_all; patch_all()
import sys
sys.path.append('/' + '/'.join(sys.path[0].split('/')[:-1]))

import logging
from .base.log import logger

log = logging.getLogger(__name__)


log.info(
    '\n'
    '\n'
    '                   _oo0oo_\n'
    '                  o8888888o\n'
    '                  88" . "88\n'
    '                  (| -_- |)\n'
    '                  0\  =  /0\n'
    '                ___/`---\'\___\n'
    '              .\' \\\\|     |// \'.\n'
    '             / \\\\|||  :  |||// \\\n'
    '            / _||||| -:- |||||- \\\n'
    '           |   | \\\\\\  -  /// |   |\n'
    '           | \_|  \'\'\\---/\'\'  |_/ |\n'
    '           \\  .-\\__  \'-\'  ___/-. /\n'
    '         ___\'. .\'  /--.--\  `. .\'___\n'
    '      ."" \'<  `.___\\_<|>_/___.\' >\' "".\n'
    '     | | :  `- \`.;`\ _ /`;.`/ - ` : | |\n'
    '     \\  \\ `_.   \\_ __\\ /__ _/   .-` /  /\n'
    ' =====`-.____`.___ \\_____/___.-`___.-\'=====\n'
    '                   `=---=\n'
    '\n'
    ' ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n'
    '            菩提本无树   明镜亦非台\n'
    '            本来无霸葛   何必常修改\n'
)


try:
    __import__('config')
except:
    log.info('Custom Config Not Found.')
else:
    log.info('Load Custom Config.')
