# -*- coding: utf-8 -*-
'''
Created on 2017年5月24日

@author: chenyitao
'''

from ..model_base import QuickModelBase


class MouldsBase(QuickModelBase):

    default_values = {'package': None,
                      'moulds': None,
                      'version': None,
                      'md5': None}


class RulesBase(QuickModelBase):

    default_values = {'platform': None,
                      'models': None}

    def __init__(self, **kwargs):
        super(RulesBase, self).__init__(**kwargs)
        items = self.__dict__.get('models')
        if not items:
            return
        modeles = []
        for item in items:
            mould = MouldsBase(**item)
            modeles.append(mould)
        self.__dict__['models'] = modeles


def main():
    kwargs = {'platform': 'cheok',
              'modules': [{'package': 'cheok_homepage',
                           'moulds': ['CheokHomepage'],
                           'version': '1.1',
                           'md5': '12345678901234567890123456789012'},
                          {'package': 'cheok_list',
                           'moulds': ['CheokList'],
                           'version': '1.2',
                           'md5': 'qwertyuiopasdfghjklzxcvbnm123456'}]}
    m = RulesBase(**kwargs)
    print(m)

if __name__ == '__main__':
    main()