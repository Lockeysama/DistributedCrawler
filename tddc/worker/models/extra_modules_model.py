# encoding: utf-8
"""
@version: ??
@author: chenyitao
@license: Apache Licence 
@software: PyCharm
@file: online_config_event_model.py
@time: 2019-03-06 13:43
"""
from ..define.event import ExtraModuleUpdate

from .event_model import EventBase


class ExtraModuleEvent(EventBase):

    fields = [
        's_owner', 's_platform', 's_feature', 's_package', 's_mould',
        's_version', 's_file_md5', 'b_valid', 'i_timestamp', 's_source'
    ]

    event = ExtraModuleUpdate

    name = 'ExtraModuleUpdate'

    desc = 'ExtraModuleUpdate'
