# encoding: utf-8
"""
@version: ??
@author: chenyitao
@license: Apache Licence 
@software: PyCharm
@file: online_config_event_model.py
@time: 2019-03-06 13:43
"""
from ..define.event import OnlineConfigFlush

from .event_model import EventBase


class OnlineConfigEvent(EventBase):

    fields = [
        's_type'
    ]

    event = OnlineConfigFlush

    name = 'OnlineConfigFlush'

    desc = 'OnlineConfigFlush'
