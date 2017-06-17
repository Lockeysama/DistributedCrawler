# -*- coding: utf-8 -*-
'''
Created on 2017年5月26日

@author: chenyitao
'''

from ..model_base import QuickModelBase


class ModuleBase(QuickModelBase):

    @staticmethod
    def members():
        return dict(QuickModelBase.members(),
                    **{'package': None,
                       'moulds': None,
                       'version': None,
                       'md5': None})
