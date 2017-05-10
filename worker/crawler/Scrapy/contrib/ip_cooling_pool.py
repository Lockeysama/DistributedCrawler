# coding: utf-8
'''
Created on 2017年4月3日

@author: chenyitao
'''

import threading
import time
import random
import gevent

from common.queues import PLATFORM_PROXY_QUEUES


class CoolingQueue(object):
    
    def __init__(self):
        self.cur_timestamp = time.time()
        self._lock = threading.Lock()
        self._list = list()
        self._ips = list()
    
    def push(self, item):
        if self._lock.acquire():
            self._list.append({item: self.cur_timestamp})
            self._ips.append(item)
            self._lock.release()
        return True
    
    def pop(self, info):
        if self._lock.acquire():
            self._list.remove(info)
            self._ips.remove(info.keys()[0])
            self._lock.release()
    
    def qlist(self):
        return self._list

    def ips(self):
        return self._ips
    

class IPCoolingPoll(object):
    '''
    classdocs
    '''

    def __init__(self, cooldown=3):
        '''
        Constructor
        '''
        self._cur_timestamp = 0
        self._ip_cooling_pool = CoolingQueue()
        self.cooldown = cooldown
        gevent.spawn(self.run)
        gevent.sleep()
    
    def push(self, item):
        self._ip_cooling_pool.push(item)
    
    def ips(self):
        return set(self._ip_cooling_pool.ips())
    
    def in_pool(self, item):
        return len(list(self.ips() & set([item])))
    
    def run(self):
        times = 0
        time_space = 0.5
        while True:
            gevent.sleep(time_space)
            self._ip_cooling_pool.cur_timestamp += time_space
            if times % 10 == 0:
                self._cur_timestamp = time.time()
                self._ip_cooling_pool.cur_timestamp = self._cur_timestamp
            times += 1
            ip_pool = self._ip_cooling_pool.qlist()[:]
            if not len(ip_pool):
                continue
            self._cur_timestamp += time_space
            random_time = random.uniform(-1, 2)
            for i in range(0, len(ip_pool)):
                info = ip_pool[i]
                ip, platform = info.keys()[0]
                use_timestamp = info[(ip, platform)]
                if self._cur_timestamp - use_timestamp >= (self.cooldown) + random_time:
                    self._ip_cooling_pool.pop(info)
                    PLATFORM_PROXY_QUEUES.get(platform, set()).add(ip)


if __name__ == '__main__':
    cooling_pool = IPCoolingPoll()
    cnt = 30
    while cnt != 0:
        cooling_pool.push('192.168.1.{cnt}'.format(cnt=cnt))
        time.sleep(0.3)
        cnt -= 1
    cooling_pool.join()
        