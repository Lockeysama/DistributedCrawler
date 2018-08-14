# -*- coding: utf-8 -*-
"""
@author  : chenyitao
@email   : yt.chen@bshier.com
@license: Apache Licence
@software: PyCharm
@file    : snowflake.py
@time    : 2018/8/13 18:16
"""
import time

from tddc import Singleton


class SnowFlakeID(object):

    __metaclass__ = Singleton

    twepoch = 1420041600000L

    sequence_bits = 12L

    worker_id_bits = 10L

    worker_id_shift = 12L

    timestamp_left_shift = 22L

    def __init__(self, worker_id=512):
        self.worker_id = worker_id
        self.sequence = 0L
        self.max_worker_id = -1L ^ (-1L << self.worker_id_bits)
        self.sequence_mask = -1L ^ (-1L << self.sequence_bits)
        self.last_timestamp = -1L

    def _time_gen(self):
        return long(int(time.time() * 1000))

    def _till_next_millis(self, last_timestamp):
        timestamp = self._time_gen()
        while timestamp <= last_timestamp:
            timestamp = self._time_gen()

        return timestamp

    def _next_id(self):
        timestamp = self._time_gen()

        if self.last_timestamp == timestamp:
            self.sequence = (self.sequence + 1) & self.sequence_mask
            if self.sequence == 0:
                timestamp = self._till_next_millis(self.last_timestamp)
        else:
            self.sequence = 0

        self.last_timestamp = timestamp

        new_id = ((timestamp - self.twepoch) << self.timestamp_left_shift) | (
                             self.worker_id << self.worker_id_shift) | self.sequence
        return new_id

    def get_sequence(self):
        return self.sequence

    def get_worker_id(self):
        return self.worker_id

    def get_timestamp(self):
        return self._time_gen()

    def get_id(self):
        new_id = self._next_id()
        return new_id

    @classmethod
    def parse(cls, sf_id):
        b_sf_id = bin(sf_id)[2:]
        id_len = len(b_sf_id)
        sequence_start = 0 if id_len < cls.worker_id_shift else id_len - cls.worker_id_shift
        sequence = b_sf_id[sequence_start:id_len]
        sequence_int = int(sequence, 2)
        worker_start = 0 if id_len < cls.timestamp_left_shift else id_len - cls.timestamp_left_shift
        worker_id = "0" if sequence_start == 0 else b_sf_id[worker_start:sequence_start]
        worker_id_int = int(worker_id, 2)
        timestamp = "0" if worker_start == 0 else b_sf_id[0:worker_start]
        ts = long(timestamp, 2)
        ts += cls.twepoch
        return ts, sequence_int, worker_id_int
