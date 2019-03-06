# -*- coding: utf-8 -*-
"""
@author  : chenyitao
@email   : yt.chen@bshier.com
@license: Apache Licence
@software: PyCharm
@file    : mysqlex.py
@time    : 2018/11/6 17:14
"""
import logging

import six

from ..base.util import Singleton
from ..base.mysql import MySQLHelper

log = logging.getLogger(__name__)


@six.add_metaclass(Singleton)
class MySQLEx(MySQLHelper):
    """
    消息队列
    """

    def __init__(self, nodes=None, tag='default'):
        super(MySQLEx, self).__init__(nodes or self.nodes(tag))

    def nodes(self, tag):
        from .online_config import OnlineConfig
        node = getattr(OnlineConfig().mysql, tag)
        return node
