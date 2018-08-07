# encoding: utf-8
"""
@version: ??
@author: chenyitao
@license: Apache Licence 
@software: PyCharm
@file: time_helper.py
@time: 2018/4/12 21:48
"""
import datetime
import time

import pytz


class TimeHelper(object):

    def __init__(self, timestamp):
        self.timestamp = None
        self.localtime = None
        self.update(timestamp)

    def update(self, timestamp):
        self.timestamp = str(timestamp).strip('.')[:10]
        self.localtime = time.localtime(int(self.timestamp))

    def get_year(self):
        return self.localtime.tm_year

    def get_month(self):
        return self.localtime.tm_mon

    def get_day(self):
        return self.localtime.tm_mday

    def get_hour(self):
        return self.localtime.tm_hour

    def get_minutes(self):
        return int(self.localtime.tm_min)

    def get_seconds(self):
        return self.localtime.tm_sec

    def get_week(self):
        return self.localtime.tm_wday

    def get_y_m_d(self):
        return '%s-%s-%s' % (self.get_year(), self.get_month(), self.get_day())

    def is_zero(self):
        return self.get_hour() == 0 and self.get_minutes() == 0 and self.get_seconds() < 59

    def is_zero_sub_1seconds(self):
        return self.get_hour() == 23 and self.get_minutes() == 59 and self.get_seconds() < 59

    def get_day_timestamp(self):
        time_array = time.strptime(self.get_y_m_d(), "%Y-%m-%d")
        return int(time.mktime(time_array))

    def get_minute_timestamp(self):
        time_array = time.strptime('%s %s:%s' % (self.get_y_m_d(),
                                                 self.get_hour(),
                                                 self.get_minutes()),
                                   "%Y-%m-%d %H:%M")
        return int(time.mktime(time_array))

    def get_5min_area_timestamp(self):
        return self.get_minute_timestamp() - ((self.get_minutes() % 5) * 60)

    def get_15min_area_timestamp(self):
        return self.get_minute_timestamp() - ((self.get_minutes() % 15) * 60)

    def get_30min_area_timestamp(self):
        return self.get_minute_timestamp() - ((self.get_minutes() % 30) * 60)

    def get_1h_area_timestamp(self):
        return self.get_minute_timestamp() - ((self.get_minutes() % 60) * 60)

    def get_4h_area_timestamp(self):
        time_array = time.strptime('%s %s:0' % (self.get_y_m_d(),
                                                self.get_hour() - self.get_hour() % 4),
                                   "%Y-%m-%d %H:%M")
        return int(time.mktime(time_array))

    def utc(self, utc_format='%Y-%m-%dT%H:%M:%S.000Z'):
        local_tz = pytz.timezone('Asia/Chongqing')
        local_format = "%Y-%m-%d %H:%M:%S"
        time_str = time.strftime(local_format, time.localtime(local_ts))
        dt = datetime.datetime.strptime(time_str, local_format)
        local_dt = local_tz.localize(dt, is_dst=None)
        utc_dt = local_dt.astimezone(pytz.utc)
        return utc_dt.strftime(utc_format)
