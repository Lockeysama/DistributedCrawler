# -*- coding: utf-8 -*-
"""
@author  : chenyitao
@email   : yt.chen@bshier.com
@license: Apache Licence
@software: PyCharm
@file    : task_pad.py
@time    : 2018/9/18 14:00
"""
import sys
from collections import defaultdict
from os import getpid, kill

import logging

import gevent.queue
import six

from ..base.util import Singleton, Device
from ..default_config import default_config

from .event import EventCenter
from .models.keep_task_model import KeepTaskEvent, KeepTaskStatus, KeepTask
from .models.event_model import Event
from .extern_modules import ExternManager

log = logging.getLogger(__name__)


@six.add_metaclass(Singleton)
class KeepTaskManager(object):

    def __init__(self):
        log.info('Keep Task Manager Is Starting.')
        super(KeepTaskManager, self).__init__()
        self._process = defaultdict(lambda: defaultdict())
        log.info('Keep Task Manager Was Started.')

    @staticmethod
    @EventCenter.route(KeepTaskEvent)
    def _task_status_change(event):
        if getpid() != default_config.PID:
            return
        log.info('Long Task Status Changed...')
        ret = KeepTaskManager().task_status_change(event)
        event.set_state(
            Event.Status.Executed_Success if ret else Event.Status.Executed_Failed
        )

    def task_status_change(self, event):
        task = KeepTask(**event.data.to_dict())
        if not task:
            log.warning('Task Not Found.{}'.format(event))
            return False
        if task.b_valid:
            self.start_task(task)
            task.state.set_state(KeepTaskStatus.Running)
        else:
            self.stop_task(task)
            task.state.set_state(KeepTaskStatus.Stop)
        return True

    def start_task(self, task):
        if task.i_state == KeepTaskStatus.Dispatched:
            identifier = '{}|{}'.format(Device.mac(), default_config.FEATURE)
            if task.s_head != identifier:
                return
            log.info('Task({}) Status Change(Start)...'.format(task.s_feature))
            pid = self._process.get(task.s_platform, {}).get(task.s_feature)
            if pid:
                kill(pid, 9)
                if sys.version > '3':
                    self._process[task.s_platform].pop(task.s_feature)
                else:
                    del self._process[task.s_platform][task.s_feature]
            module = ExternManager().get_model(task.s_platform, task.s_feature)
            if not module:
                log.warning('[{}:{}] Module Not Found.'.format(task.s_platform, task.s_feature))
                return
            pid = gevent.fork()
            if pid:
                self._process[module.platform][module.feature] = pid
            else:
                try:
                    m = module(task)
                    m.run()
                except Exception as e:
                    log.warning(e)
            gevent.sleep()

    def stop_task(self, task):
        pid = self._process.get(task.s_platform, {}).get(task.s_feature)
        if pid:
            try:
                log.info('Task({}) Status Change(Stop)...'.format(task.s_feature))
                kill(pid, 9)
                if sys.version > '3':
                    self._process[task.s_platform].pop(task.s_feature)
                else:
                    del self._process[task.s_platform][task.s_feature]
            except Exception as e:
                log.warning(e)
