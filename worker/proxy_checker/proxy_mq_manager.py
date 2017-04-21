# -*- coding: utf-8 -*-
'''
Created on 2017年4月20日

@author: chenyitao
'''

from base.task.task_manager_base import TaskManagerBase
from conf.proxy_checker_site import PROXY_CHECKER_EVENT_TOPIC_NAME, PROXY_CHECKER_EVENT_TOPIC_GROUP

SIGNAL_TASK_MANAGER_READY = object()


class ProxyMQManager(TaskManagerBase):
    '''
    classdocs
    '''
    event_topic_name = PROXY_CHECKER_EVENT_TOPIC_NAME
    
    event_topic_group = PROXY_CHECKER_EVENT_TOPIC_GROUP


def main():
    from conf.base_site import STATUS
    import gevent.monkey
    gevent.monkey.patch_all()
    
    ProxyMQManager()
    
    while STATUS:
        gevent.sleep(60)

if __name__ == '__main__':
    main()
