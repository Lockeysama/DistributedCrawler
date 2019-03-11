# encoding: utf-8
"""
@version: ??
@author: chenyitao
@license: Apache Licence 
@software: PyCharm
@file: models.py
@time: 2018/10/10 20:06
"""

from ......base.util import JsonObjectSerialization


class ProxyTask(JsonObjectSerialization):

    fields = [
        's_url', 's_platform', 's_feature', 'i_status', 's_headers', 's_method',
        's_params', 's_json', 'b_valid', 's_data', 's_cookies', 's_proxy', 'i_timeout'
    ]
