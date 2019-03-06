# -*- coding: utf-8 -*-
"""
Created on 2017年4月14日
@author: chenyitao
"""
import logging

import gevent

from ..online_config import OnlineConfig
from ..timing_task_manager import TimingTaskManager
from ..timing_task_model import TimingTaskStatus

from .downloader import Downloader, SpiderBase

log = logging.getLogger(__name__)


class TimingCrawler(SpiderBase):
    """
    Spider管理、任务分配
    """

    def __init__(self):
        """
        Constructor
        """
        log.info('Spider Is Starting.')
        super(TimingCrawler, self).__init__()
        self.task_conf = type('TaskConfig', (), OnlineConfig().task.default)
        self._spider = Downloader(self, TimingTaskManager().conf.queue_size)
        gevent.spawn_later(3, self._task_dispatch)
        gevent.sleep()
        log.info('Spider Was Started.')

    def _task_dispatch(self):
        while True:
            # 队列中获取任务
            task = TimingTaskManager().get()
            self._spider.add_task(task)

    def task_wait(self, task):
        if not task.filter.filter(TimingTaskManager().filter_table):
            task.set_attr_to_remote('s_priority', 'low')
            task.state.set_state(TimingTaskStatus.CrawlTopic)
            task.recover.stop()
            TimingTaskManager().push_task(task)
        del task

    def task_success(self, task):
        TimingTaskManager().task_success(task)
        del task

    def task_failed(self, task):
        TimingTaskManager().task_failed(task)
        del task
