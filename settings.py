# -*- coding: utf-8 -*-
'''
Created on 2017年6月15日

@author: chenyitao
'''

from enum import Enum


# Test
TEST = True

# Client ID
CLIENT_ID = 1

Worker = Enum('Worker', ('Crawler',
                         'Parser',
                         'ProxyChecker',
                         'CookiesGenerator',
                         'Monitor'))

# Current Worker
# WORKER = Worker.Crawler
WORKER = Worker.Parser
# WORKER = Worker.ProxyChecker
# WORKER = Worker.CookiesGenerator
# WORKER = Worker.Monitor