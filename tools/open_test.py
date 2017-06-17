# -*- coding: utf-8 -*-
'''
Created on 2017年6月5日

@author: chenyitao
'''

from lxml import html

def load_test():
    with open('/Users/chenyitao/git/open_test/test.html', 'r') as f:
        content = f.read()
    ret = html.fromstring(content)
    return ret

def main():
    doc = load_test()
    bodys = doc.xpath('//*[@class="TestItemBody"]')
    for body in bodys:
        
    print(bodys)

if __name__ == '__main__':
    main()
