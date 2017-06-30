# -*- coding: utf-8 -*-
'''
Created on 2017年6月30日

@author: chenyitao
'''

from .base import ExceptionModelBase, ExceptionType


class ParserClientException(ExceptionModelBase):

    EXCEPTION_TYPE = ExceptionType.Parser.CLIENT


class ParserTaskFailedException(ExceptionModelBase):

    EXCEPTION_TYPE = ExceptionType.Parser.TASK_FAILED


class ParserTaskNoParseModelException(ExceptionModelBase):

    EXCEPTION_TYPE = ExceptionType.Parser.TASK_NO_PARSE_MODEL


class ParserSrorageFailedException(ExceptionModelBase):

    EXCEPTION_TYPE = ExceptionType.Parser.STORAGE_FAILED


class ParserStoragerException(ExceptionModelBase):

    EXCEPTION_TYPE = ExceptionType.Parser.STORAGER_EXCEPTION
