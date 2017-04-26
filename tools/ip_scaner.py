# coding: utf-8
'''
Created on 2017年3月14日

@author: chenyitao
'''
import gevent
from gevent import monkey
monkey.patch_all();
from lxml import html, etree
import requests
import threading
import Queue
import time
import socket
import urllib2

# 117.90.*.*:9000
# 27.148.151.*:80
# 121.232
# 61.133

ports = [80, 1080, 8080, 8090, 8998, 808, 9000, 8123, 8118]

areas = []

ips = Queue.Queue()

port_opened_ips = Queue.Queue()

op_ips = {}

corourine_num = 1024

lock = threading.Lock()

def response_check(response):
    if response.status_code != 200:
        return False
    else:
        try:
            doc = html.document_fromstring(response.text)
        except Exception, e:
            print(e)
        else:
            ret = doc.xpath('//*[@class="module-title"]')
            if len(ret):
                return True
    return False

def check_proxy():
    while True:
        host, port = port_opened_ips.get()
        useful = False
        proxies = {'http': host + ':' + str(port)}
        headers = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) '
                                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                                  'Chrome/56.0.2924.87 Safari/537.36'),
                    'X-Forwarded-For': proxies['http'],
                    'X-Real-IP': proxies['http']}
        try:
            rsp = requests.get('http://www.cheok.com/', proxies=proxies, timeout=5, headers=headers)
        except Exception, e:
            print(e)
        else:
            useful = response_check(rsp)
        finally:
            if useful:
                lock.acquire()
                with open('ips.txt', 'a') as f:
                    f.write(host + ':' + str(port) + '\n')
                lock.release()

def check_port(host, port):
    try:
        _s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        _s.settimeout(2)
        _s.connect((host, int(port)))
        _s.close()
        return True
    except:
        return False

def get_ip_area():
    global areas
    data = urllib2.urlopen('http://ipcn.chacuo.net/view/i_CHINANET').read()
    if data is not None:
        tree = etree.HTML(data)
        dds = tree.findall('.//dd')
        for dd in dds:
            area = dd.findall('.//span')
            areas.append([area[0].text, area[1].text])

def ip_maker():
    global areas
    get_ip_area()
    while len(areas):
        area = areas.pop(0)
        l_area = area[0].split('.')
        r_area = area[1].split('.')
        for i in range(int(l_area[0]), int(r_area[0])+1):
            for j in range(int(l_area[1]), int(r_area[1])+1):
                if int(l_area[2]) < 59 and int(l_area[3]) < 248:
                    continue
                for k in range(int(l_area[2]), int(r_area[2])+1):
                    for l in range(int(l_area[3]), int(r_area[3])+1):
                        ip = '{0}.{1}.{2}.{3}'.format(i, j, k, l)
                        ips.put(ip)
                    yield ip

def scan():
    while True:
        ip = ips.get()
        for port in ports:
            if check_port(ip, port):
                if not op_ips.get(ip):
                    op_ips[ip] = []
                op_ips[ip].append(port)
                port_opened_ips.put((ip, port))
        if op_ips.get(ip):
            print(ip,op_ips[ip])
            print('CurNum: %d' % len(op_ips))
            

def start():
    global corourine_num
    for _ in xrange(corourine_num):
        gevent.spawn(scan)
        gevent.sleep()
    for _ in xrange(16):
        gevent.spawn(check_proxy)
        gevent.sleep()
    ip_fac = ip_maker()
    for ip in ip_fac:
        tag = str(ips.qsize()) + ' {0} '.format(ip) + time.asctime(time.localtime(time.time()))
        print(tag)
        with open('valid.txt', 'a') as f:
            f.write(tag + '\n')
        while not ips.qsize() < corourine_num*2:
            time.sleep(0.5)

if __name__ == '__main__':
    start()
    print('Done')
