# -*- coding: utf-8 -*-
"""
@author  : chenyitao
@email   : yt.chen@bshier.com
@license: Apache Licence
@software: PyCharm
@file    : JosnObjectSerialization.py
@time    : 2018/9/18 14:55
"""
import json


class JsonObjectSerialization(object):

    fields = None

    def __init__(self, fields=None, **kwargs):
        if not fields and not self.fields:
            raise Exception(message='Fields Not Found.')
        for k in self.fields:
            self.__dict__[k] = kwargs.get(k, None)

    def to_dict(self):
        return {k: self.__dict__.get(k) for k in self.fields if self.__dict__.get(k) is not None}

    def to_json(self):
        return json.dumps(self.to_dict())

    def __str__(self):
        return str(self.to_dict())
