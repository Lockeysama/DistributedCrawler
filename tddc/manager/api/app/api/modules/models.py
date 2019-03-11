# encoding: utf-8
"""
@version: ??
@author: chenyitao
@license: Apache Licence 
@software: PyCharm
@file: models.py
@time: 2018/3/28 17:42
"""
from ......base.util import JsonObjectSerialization


class Module(JsonObjectSerialization):

    fields = [
        's_owner', 's_platform', 's_feature', 's_package', 's_mould',
        's_version', 's_file_md5', 'b_valid', 'i_timestamp', 's_source'
    ]
