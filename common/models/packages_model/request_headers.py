# -*- coding: utf-8 -*-
'''
Created on 2017年5月24日

@author: chenyitao
'''

from common.models.packages_model.package_model import QuickModelBase


class RequestHeadersModels(QuickModelBase):

    @staticmethod
    def members():
        return dict(QuickModelBase.members(),
                    **{'platform': None,
                       'Proxy': None,
                       'Host': None,
                       'User-Agent': None,
                       'Accept': None,
                       'Accept-Encoding': None,
                       'Accept-Language': None,
                       'Cookie': None,
                       'Referer': None,
                       'Cache-Control': None,
                       'Connection': None,
                       'DNT': None,
                       'Upgrade-Insecure-Requests': None,
                       'X-Requested-With': None,
                       'post_params': None})
