# -*- coding: utf-8 -*-
'''
Created on 2017年6月30日

@author: chenyitao
'''

from .base import ExceptionModelBase, ExceptionType


class ProxyCheckerClientException(ExceptionModelBase):

    EXCEPTION_TYPE = ExceptionType.ProxyChecker.CLIENT


class ProxyCheckerSrorageFailedException(ExceptionModelBase):

    EXCEPTION_TYPE = ExceptionType.ProxyChecker.STORAGE_FAILED


class ProxyCheckerStoragerException(ExceptionModelBase):

    EXCEPTION_TYPE = ExceptionType.ProxyChecker.STORAGER_EXCEPTION


class ProxyCheckerNoSrcProxyException(ExceptionModelBase):

    EXCEPTION_TYPE = ExceptionType.ProxyChecker.NO_SRC_PROXY


class ProxyCheckerCheckeFailedException(ExceptionModelBase):

    EXCEPTION_TYPE = ExceptionType.ProxyChecker.CHECKE_FAILED
