# encoding: utf-8
"""
@version: ??
@author: chenyitao
@license: Apache Licence 
@software: PyCharm
@file: keep_module_extra.py
@time: 2019-03-05 14:53
"""
import setproctitle

from ....default_config import default_config
from ..extern_base import ExternBase


class KeepModuleExtra(ExternBase):

    def __init__(self, task, *args, **kwargs):
        super(KeepModuleExtra, self).__init__()
        self.task = task
        setproctitle.setproctitle(
            'TDDC-{}-{}'.format(default_config.PLATFORM, self.feature)
        )
