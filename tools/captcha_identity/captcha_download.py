# -*- coding: utf-8 -*-
'''
Created on 2017年5月10日

@author: chenyitao
'''
import requests
import time

def main():
    cnt = 1
    while cnt <= 100:
        # http://shixin.court.gov.cn/captchaNew.do?captchaId=a56e973232f741018a07513c3c2af9e8&random=0.5754127154653328
        # https://passport.cocos.com/php-captcha/captcha_code_file.php?rand=1166424099
        rsp = requests.get('http://shixin.court.gov.cn/captchaNew.do?captchaId=a56e973232f741018a07513c3c2af9e8&random=0.5754127154653328')
        with open('./captchas/test3/%d.jpeg' % cnt, 'wb') as f:
            f.write(rsp.content)
        print(cnt)
        cnt += 1
        time.sleep(1)

if __name__ == '__main__':
    main()
