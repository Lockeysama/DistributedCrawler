# -*- coding: utf-8 -*-
"""
Created on 2017年4月18日

@author: chenyitao
"""

import hashlib
import logging

from lxml import html
import json

from ..extern_base import ExternBase

log = logging.getLogger(__name__)


class ParseRuleBase(ExternBase):
    """
    classdocs
    """
    
    JSON = 'JSON'
    
    HTML = 'HTML'

    def __init__(self, task, body):
        """
        Constructor
        """
        super(ParseRuleBase, self).__init__()
        # manage task_list
        self._task = task
        self._body = body
        self._body_type = None
        self.items = dict()
        self.tasks = list()
        self._md5_mk = hashlib.md5()
        if body[0] == '{' and body[-1] == '}' or body[0] == '[' and body[-1] == ']':
            try:
                self._json_dict = json.loads(body)
            except Exception as e:
                log.exception(e)
            else:
                self._body_type = self.JSON
        else:
            self._doc = html.document_fromstring(body)
            self._body_type = self.HTML
        self._parse()
        
    def _parse(self):
        raise NotImplementedError
    
    def _xpath(self, xp):
        if self._body_type == self.HTML:
            return self._doc.xpath(xp)
        return None
    
    def _get(self, key, default=None):
        if self._body_type == self.JSON:
            return self._json_dict.get(key, default)
        return None
