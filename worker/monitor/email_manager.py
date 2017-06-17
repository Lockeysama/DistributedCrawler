# -*- coding: utf-8 -*-
'''
Created on 2017年5月17日

@author: chenyitao
'''

import time
import smtplib
from conf.monitor_site import MAIL_USER, MAIL_PWD, MAIL_TO, MAIL_HOST, MAIL_PORT
from email.mime.text import MIMEText
from common import TDDCLogging


class EMailManager(object):
    '''
    classdocs
    '''
    
    last_send_time = 0

    @staticmethod
    def send_mail(subject, content):
        cur_time = time.time()
        if EMailManager.last_send_time > cur_time - 60:
            return False
        msg = MIMEText(content, 'plain', 'utf-8')
        msg['Subject'] = subject
        msg['From'] = MAIL_USER
        msg['To'] = ';'.join(MAIL_TO)
        server = smtplib.SMTP_SSL(MAIL_HOST, MAIL_PORT)
        try:
            server.login(MAIL_USER, MAIL_PWD)
            server.sendmail(MAIL_USER, MAIL_TO, msg.as_string())
        except Exception, e:
            TDDCLogging.error(e)
        else:
            TDDCLogging.info('EMAIL[%s] Send Success.' % subject)
            EMailManager.last_send_time = cur_time
            return True
        finally:
            server.close()

        
def main():
    EMailManager.send_mail('TDDC[Exception Test]', 'Mail Test2.')
    EMailManager.send_mail('TDDC[Exception Test]', 'Mail Test3.')
    while True:
        time.sleep(10)

if __name__ == '__main__':
    main()
