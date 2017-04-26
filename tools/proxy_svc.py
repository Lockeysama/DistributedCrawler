# -*- coding: utf-8 -*-
'''
Created on 2017年4月21日

@author: chenyitao
'''

import socket  
import time

apaaddr=('127.0.0.1',8888)
apaser=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

seraddr=('127.0.0.1',9995)  
ser=socket.socket(socket.AF_INET,socket.SOCK_STREAM)  
ser.bind(seraddr)  
ser.listen(5)  
poll=[]  
while True:  
    con,addr=ser.accept()  
    poll.append(con)  
  
    while len(poll):
        buf = None
        c=poll.pop(0)  
        buf=c.recv(4096)  
        if not buf:  
            break
        apaser.connect(apaaddr)  
        x = apaser.send(buf)
        data=apaser.recv(4096)
        y = c.send(data)
        time.sleep(0.5)
        c.close()  
        time.sleep(0.5)
        apaser.close() 
        time.sleep(0.5)

def main():
    pass

if __name__ == '__main__':
    main()
