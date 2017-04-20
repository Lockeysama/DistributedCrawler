# -*- coding: utf-8 -*-
'''
Created on 2017年4月12日

@author: chenyitao
'''

from common.simple_tools import enum

WorkerModel = enum(CRAWLER=0,
                   PARSER=1,
                   PROXY_CHECKER=2)

def main():
    print(WorkerModel.CRAWLER, WorkerModel.PARSER)

if __name__ == '__main__':
    main()