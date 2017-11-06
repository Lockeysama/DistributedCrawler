# -*- coding: utf-8 -*-
'''
Created on 2017年5月24日

@author: chenyitao
'''

from .package_model import QuickModelBase


class MonitorEMailModels(QuickModelBase):

    @staticmethod
    def members():
        return dict(QuickModelBase.members(),
                    **{'user': None,
                       'passwd': None,
                       'to': None,
                       'host': None,
                       'port': None})
