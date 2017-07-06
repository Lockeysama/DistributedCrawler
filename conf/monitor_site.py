# -*- coding: utf-8 -*-
'''
Created on 2017年5月17日

@author: chenyitao
'''
from .base_site import BaseSite

class MonitorSite(BaseSite):
    
    EXCEPTION_GROUP = 'tddc.exception'

    MAIL_HOST = 'smtp.exmail.qq.com'
    
    MAIL_PORT = 465
    
    MAIL_USER = 'reptile_monitor@51tuodao.com'
    
    MAIL_PWD = 'Tddc2017'
    
    MAIL_TO = ['chenyitao@51tuodao.com']

