# -*- coding:utf-8 -*
'''
Created on 2017年4月10日

@author: chenyitao
'''

import random
import gevent
import json
from thrift.transport import TSocket  
from thrift.transport import TTransport
from hbase import THBaseService  
from hbase.ttypes import TColumnValue, TPut, TGet, TColumn
from thrift.transport.TTransport import TTransportException
from thrift.protocol.TCompactProtocol import TCompactProtocol
from common import TDDCLogging


class HBaseManager(object):
    '''
    classdocs
    '''

    def __init__(self, host_ports, callback=None):
        '''
        Constructor
        '''
        self._callback = callback
        self._status = False
        self._host_ports = list(host_ports)
        self._host_ports_pool = list(self._host_ports)
        self._connect()
        gevent.spawn(self._keep_alive)
        gevent.sleep()
        
    def _connect(self):
        try:
            self._current_host_port = random.choice(self._host_ports_pool).split(':')
            self._sock = TSocket.TSocket(host=self._current_host_port[0],
                                         port=self._current_host_port[1])
            self._transport = TTransport.TFramedTransport(self._sock)
            self._protocol = TCompactProtocol(self._transport)
            self._client = THBaseService.Client(self._protocol)
            self._transport.open()
        except Exception, e:
            print(e)
            current_host_port = ':'.join(self._current_host_port)
            self._host_ports_pool.remove(current_host_port)
            if len(self._host_ports_pool) > 0:
                TDDCLogging.warning('HBase Server Exception. Now Is Reconnecting.')
            else:
                TDDCLogging.warning('HBase Server Fatal Error. Please Check It.')
                gevent.sleep(30)
                self._host_ports_pool = list(self._host_ports)
                TDDCLogging.warning('Retry Connecting HHase.')
            self._reconnect()
        else:
            self._host_ports_pool = list(self._host_ports)
            self._status = True
            TDDCLogging.info('----->HBase Is Connected.(%s)' % ':'.join(self._current_host_port))
            self._hbase_was_ready()

    def _hbase_was_ready(self):
        if self._callback:
            self._callback()
        
    def _keep_alive(self):
        while True:
            gevent.sleep(5)
            try:
                if self._status:
                    if not self.get('keep_alive', 'ping'):
                        raise TTransportException
            except TTransportException, e:
                if not self._status:
                    return
                print(e)
                self._status = False
                if len(self._host_ports_pool):
                    self._reconnect()
            except Exception, e:
                print(e)
                gevent.sleep(5)
            else:
                gevent.sleep(25)
                
    def _reconnect(self):
        self._connect()

    def put(self, table, row_key, items=None):
        if not self._status:
            TDDCLogging.warning('[Put Operation Was Failed] HBase Server Is Exception.')
            return False
        cvs = []
        for family, info in items.items():
            if not isinstance(info, dict):
                raise TypeError
            for k, v in info.items():
                if isinstance(v, list) or isinstance(v, dict):
                    v = json.dumps(v)
                cv = TColumnValue(family, k, v)
                cvs.append(cv)
        tp = TPut(row_key, cvs)
        try:
            self._client.put(table, tp)
        except Exception, e:
            print(e)
            return False
        else:
            return True

    def get(self, table_name, row_key, family=None, qualifier=None):
        if not self._status:
            TDDCLogging.warning('[Get Operation Was Failed] HBase Server Is Exception.')
            return None
        get = TGet()
        get.row = row_key
        if family:
            tc = TColumn()
            tc.family = family
            if qualifier:
                tc.qualifier = qualifier
            get.columns = [tc]
        try:
            ret = None
            ret = self._client.get(table_name, get)
        except Exception, e:
            print(e)
        return ret

    def close(self):
        self._transport.close()
        
    def __del__(self):
        self.close()
        
    
def main():
    from conf.base_site import HBASE_HOST_PORTS
    hbm = HBaseManager(HBASE_HOST_PORTS)
    cnt = 1
    while True:
        if cnt % 10 == 0:
            ret = hbm.get('task_test', 'fec03ab4ebda98a394752a3cb290f179')
            print('get：', ret)
        cnt += 1
        gevent.sleep(1)
    
if __name__ == '__main__':
    main()
