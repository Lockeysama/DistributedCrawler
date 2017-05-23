# -*- coding: utf-8 -*-
'''
Created on 2017年4月20日

@author: chenyitao
'''

from ..base import TaskManagerBase
from conf import ProxyCheckerSite


class ProxyMQManager(TaskManagerBase):
    '''
    classdocs
    '''
    event_topic_name = ProxyCheckerSite.EVENT_TOPIC
    
    event_topic_group = ProxyCheckerSite.EVENT_TOPIC_GROUP


def main():
    import gevent.monkey
    gevent.monkey.patch_all()
    
    ProxyMQManager()
    
    while True:
        gevent.sleep(60)

if __name__ == '__main__':
    main()
