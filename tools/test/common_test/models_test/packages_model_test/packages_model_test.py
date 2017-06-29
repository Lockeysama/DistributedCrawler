# -*- coding: utf-8 -*-
'''
Created on 2017年5月26日

@author: chenyitao
'''

from common.models.packages_model.package_model import PackageBase
from common.models.packages_model.mudule_model_base import ModuleBase
from common.models.packages_model.cookies import CookiesGeneratorModels
from common.models.packages_model.crawler import CrawlerModels
from common.models.packages_model.monitor import MonitorExceptionProcessModels, MonitorEMailModels
from common.models.packages_model.parser import ParserModels
from common.models.packages_model.proxy_checker import ProxyCheckerModels, ProxyCheckerSrcAPIModels
from common.models.packages_model.request_headers import RequestHeadersModels

kwargs = {'platform': 'cheok',
          'modules': [{'package': 'cheok_homepage',
                       'modules': ['CheokHomepage'],
                       'version': '1.1',
                       'md5': '12345678901234567890123456789012'},
                      {'package': 'cheok_list',
                       'modules': ['CheokList'],
                       'version': '1.2',
                       'md5': 'qwertyuiopasdfghjklzxcvbnm123456'}]}

headers = {}

def cls_test_package_model_base(**kwargs):
    class PackagesModelTest(PackageBase):
        
        @staticmethod
        def members():
            return dict(PackageBase.members(),
                        **{'test2': None,
                           'test3': None,
                           'test4': None})
        
        @staticmethod
        def types():
            return dict(PackageBase.types(),
                        **{'test4': ModuleBase})
    kwargs['test4'] = {'package': 'cheok_detail',
                       'modules': ['CheokDetail'],
                       'version': '1.2',
                       'md5': '12345678901234567890123456789999'}
    kwargs['test2'] = ['test22']
    kwargs['test3'] = {'test33': 1}
    m = PackagesModelTest(**kwargs)
    return m

def cls_test_cookies(**kwargs):
    m = CookiesGeneratorModels(**kwargs)
    return m

def cls_test_crawler(**kwargs):
    m = CrawlerModels(**kwargs)
    return m

def cls_test_monitor_ep(**kwargs):
    m = MonitorExceptionProcessModels(**kwargs)
    return m

def cls_test_monitor_em(**kwargs):
    m = MonitorEMailModels(**kwargs)
    return m

def cls_test_parser(**kwargs):
    m = ParserModels(**kwargs)
    return m

def cls_test_proxy_checker(**kwargs):
    m = ProxyCheckerModels(**kwargs)
    return m

def cls_test_proxy_src(**kwargs):
    m = ProxyCheckerSrcAPIModels(**kwargs)
    return m

def cls_test_request_headers(**kwargs):
    m = RequestHeadersModels(**kwargs)
    return m

def main():
    global kwargs, headers
    cls_ist = []
    cls_ist.append(cls_test_package_model_base(**kwargs))
    cls_ist.append(cls_test_cookies(**kwargs))
    cls_ist.append(cls_test_crawler(**kwargs))
    cls_ist.append(cls_test_monitor_ep(**kwargs))
    cls_ist.append(cls_test_monitor_em(**kwargs))
    cls_ist.append(cls_test_parser(**kwargs))
    cls_ist.append(cls_test_proxy_checker(**kwargs))
    cls_ist.append(cls_test_proxy_src(**kwargs))
    cls_ist.append(cls_test_request_headers(**headers))
    for ist in cls_ist:
        print('*'*10 + str(ist.__class__) + '*'*10)
        print(ist) 
        print('*'*10 + str(ist.__class__) + '*'*10 + '\n'*2)

if __name__ == '__main__':
    main()
