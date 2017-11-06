# -*- coding: utf-8 -*-
'''
Created on 2017年5月24日

@author: chenyitao
'''

from ..model_base import QuickModelBase


class ModuleModel(QuickModelBase):

    @staticmethod
    def members():
        return dict(QuickModelBase.members(),
                    **{'package': None,
                       'mould': None,
                       'feature': None,
                       'version': None,
                       'md5': None,
                       'valid': None})


class PackageModel(QuickModelBase):

    @staticmethod
    def members():
        return dict(QuickModelBase.members(),
                    **{'platform': None,
                       'packages': None})

    @staticmethod
    def types():
        return dict(QuickModelBase.types(),
                    **{'packages': [ModuleModel]})
