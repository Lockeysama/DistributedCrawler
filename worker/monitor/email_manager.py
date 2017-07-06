# -*- coding: utf-8 -*-
'''
Created on 2017年5月17日

@author: chenyitao
'''

from email.mime.text import MIMEText
import smtplib
import time

from common import TDDCLogging
from conf.monitor_site import MonitorSite


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
        msg['From'] = MonitorSite.MAIL_USER
        msg['To'] = ';'.join(MonitorSite.MAIL_TO)
        server = smtplib.SMTP_SSL(MonitorSite.MAIL_HOST,
                                  MonitorSite.MAIL_PORT)
        try:
            server.login(MonitorSite.MAIL_USER, MonitorSite.MAIL_PWD)
            server.sendmail(MonitorSite.MAIL_USER,
                            MonitorSite.MAIL_TO,
                            msg.as_string())
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
