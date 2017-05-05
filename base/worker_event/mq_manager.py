# -*- coding: utf-8 -*-
'''
Created on 2017年5月4日

@author: chenyitao
'''

import threading
from conf.base_site import STATUS
import time
import json
from base.models.event import Event
from common.queues import EVENT_QUEUE


class MQManager(threading.Thread):
    
    def __init__(self, name='mq_manager'):
        super(MQManager, self).__init__(name=name)
        self.setDaemon(True)
        self.start()
    
    def run(self):
        print('--->Event Consumer Was Ready.')
        self._ready(self._event_tag)
        while STATUS:
            msgs = self._event_consumer.poll(2)
            if not len(msgs):
                time.sleep(5)
                continue
            self._parse_msgs(msgs)
            
    def _parse_msgs(self, msgs):
        for _, records in msgs.items():
            for record in records:
                try:
                    item = json.loads(record.value)
                except Exception, e:
                    self._consume_msg_exp('JSON_ERR', record.value, e)
                else:
                    if item and isinstance(item, dict) and item.get('type', None):
                        event = Event(item)
                        EVENT_QUEUE.put(event)
                    else:
                        self._consume_msg_exp('MSG ERR', item) 

def main():
    pass

if __name__ == '__main__':
    main()
