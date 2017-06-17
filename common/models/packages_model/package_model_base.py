# -*- coding: utf-8 -*-
'''
Created on 2017年5月24日

@author: chenyitao
'''

from ..model_base import QuickModelBase
from .mudule_model_base import ModuleBase


class PackageBase(QuickModelBase):

    @staticmethod
    def members():
        return dict(QuickModelBase.members(),
                    **{'platform': None,
                       'packages': None})

    @staticmethod
    def types():
        return dict(QuickModelBase.types(),
                    **{'packages': [ModuleBase]})
