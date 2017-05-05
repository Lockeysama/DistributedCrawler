# -*- coding: utf-8 -*-
'''
Created on 2017年5月5日

@author: chenyitao
'''

def singleton(cls, *args, **kw):
    instances = {}

    def _singleton():
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]
    return _singleton

def main():
    pass

if __name__ == '__main__':
    main()
