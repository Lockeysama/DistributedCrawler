# -*- coding: utf-8 -*-
'''
Created on 2017年5月24日

@author: chenyitao
'''

from .rules_base import QuickModelBase, RulesBase


class MonitorExceptionProcessRules(RulesBase):

    pass


class MonitorEMailRules(QuickModelBase):

    default_values = {'user': None,
                      'passwd': None,
                      'to': None,
                      'host': None,
                      'port': None}


def main():
    pass

if __name__ == '__main__':
    main()
