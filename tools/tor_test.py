# -*- coding:utf-8 -*-
'''
Created by 2017.4.20

@author: slm
'''
import urllib
import urllib2
import json
import tornado.ioloop
import tornado.web
import tornado.httpclient
from tornado.httpclient import HTTPRequest
from lxml import html

class UserInfoHande(tornado.web.RequestHandler):
 
    @tornado.web.asynchronous
    def get(self, pcode):
        tornado.httpclient.AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient", max_clients=100)         
        client = tornado.httpclient.AsyncHTTPClient()
#         arg_dict = self.request.arguments
#         post_dict = {'captchaId': arg_dict['captchaId'][0],
#                      'pCardNum': None,
#                      'pCode': arg_dict['pCode'][0],
#                      'pName': arg_dict['pName'][0],
#                      'pProvince': 0}
        post_dict = {'captchaId': '1e2179d25c2f485291b09641ffc957a1',
                     'pCardNum': '',
                     'pCode': '%s'%pcode,
                     'pName': '金崇祯',
                     'pProvince': 0}
        post_data = urllib.urlencode(post_dict)
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',}
        req = HTTPRequest('http://shixin.court.gov.cn/findDisNew',
                          'POST',
                          headers,
                          body=post_data)
        client.fetch(req, callback=self.on_response)

    def on_response(self, response):
#         with open('./response.html', 'r') as f:
#             data = f.read()

        self.write(response.body)
        self.finish()

class UrllibHandle(tornado.web.RequestHandler):
    def get(self):
#         self.write('ddd')
        arg_dict = self.request.arguments
        post_dict = {'captchaId': arg_dict['captchaId'][0],
                     'pCardNum': None,
                     'pCode': arg_dict['pCode'][0],
                     'pName': arg_dict['pName'][0],
                     'pProvince': 0}
        data = self.get_info(post_dict)
        self.write(data)
    
    def get_info(self, post_dict):
        post_url = 'http://shixin.court.gov.cn/findDisNew'
        post_dict = {'captchaId': '950241a1db714cd895396251577be861',
                     'pCardNum': None,
                     'pCode': 'xydq',
                     'pName': '张小明',
                     'pProvince': 0}
        post_data = urllib.urlencode(post_dict)
        list_info = self.start_request(post_url, post_data)
        
        with open('./response.html', 'r') as f:
            list_info = f.read()
            
        doc = html.fromstring(list_info)
        info_list = doc.xpath('//div[@id="ResultlistBlock"]//td//a[@id]//@id')
        if len(info_list)>0:
            url = 'http://shixin.court.gov.cn/disDetailNew?id=%s&pCode=%s&captchaId=%s'%(info_list[0],
                                                                                         post_dict['pCode'],
                                                                                         post_dict['captchaId'])
            result = self.start_request(url, None)
            return result
        else:
            return list_info
   
    def start_request(self, url, post_data):
        i_headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:52.0) Gecko/20100101 Firefox/52.0'}
        req = urllib2.Request(url, headers=i_headers, data=post_data)
        response = urllib2.urlopen(req, timeout=5)
        html_data = response.read()
        with open('./end.html', 'r') as f:
            html_data = f.read()
        return html_data

class MainHandler(tornado.web.RequestHandler):
    
    @tornado.web.asynchronous
    def get(self, pcode):
        tornado.httpclient.AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient", max_clients=100)         
        client = tornado.httpclient.AsyncHTTPClient()
        url = 'http://shixin.court.gov.cn/disDetailNew?id=515277794&pCode=%s&captchaId=3cd61bbfd7de4407b1181388dedade4f'%(pcode)
        url = 'http://shixin.court.gov.cn/disDetailNew?id=515277794&pCode=g8k7&captchaId=3cd61bbfd7de4407b1181388dedade4f'
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
                   'Cookie':'JSESSIONID=C7AF0D6353BEE4A43FC8DF8B7E1AAADB; _gscu_2025930969=9268032082bhp285; _gscbrs_2025930969=1; _gscu_125736681=92741833k3vee318; _gscbrs_125736681=1; _gscu_1049835508=92741835x9fy3018; _gscbrs_1049835508=1; Hm_lvt_9e03c161142422698f5b0d82bf699727=1492741836; Hm_lpvt_9e03c161142422698f5b0d82bf699727=1492741836; _gscs_2025930969=t92745531udsv3185|pv:1; ONEAPM_AI="applicationID:13||ttGuid:dc3b42a6e5423dee||queueTime:0||transactionName:D1UKNSMwHiopDxINWzYfOxEjOB4+CwMIEEY3XAQEI34GMDsFEkpQNxBAJhQFWQ==||applicationTime:0||licenseKey:a~BueYfAVaa2anVr"'}
        req = HTTPRequest(url,
                          'GET',
                          headers)
        client.fetch(req, callback=self.on_response)

    def on_response(self, response):
        self.write(response.body)
        self.finish()


class TestHandle(tornado.web.RequestHandler):
    
    @tornado.web.asynchronous
    def get(self):
        self.write('response.body')
        self.finish()
    
application = tornado.web.Application([
#     (r"/info/(.*)", MainHandler),
#     (r'/findDisNew/(.*)', UserInfoHande),
#     (r'/index',UrllibHandle),
    (r'.*', TestHandle),
    ])

def main():
    application.listen(8888, xheaders=True)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()
    