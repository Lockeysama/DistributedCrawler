# -*- coding: utf-8 -*-
"""
Created on 2017年4月11日

@author: chenyitao
"""
import logging

import gevent

from ..extern_modules import ExternManager
from ..online_config import OnlineConfig
from ..timing_task_manager import TimingTaskManager
from tddc.worker.models.timing_task_model import TimingTaskStatus
from ..redisex import RedisEx
from ..storager import Storager

log = logging.getLogger(__name__)


class TimingParser(object):
    """
    数据抽取控制
    """

    def __init__(self):
        """
        Constructor
        """
        log.info('Parser Is Starting.')
        self.task_conf = type('TaskConfig', (), OnlineConfig().task.default)
        super(TimingParser, self).__init__()
        gevent.spawn_later(3, self._parse)
        gevent.sleep()
        log.info('Parser Was Ready.')

    def _parse(self):
        while True:
            task = TimingTaskManager().get()
            cls = ExternManager().get_model(task.s_platform, task.s_feature)
            if not cls:
                task.i_state = TimingTaskStatus.ParseModuleNotFound
                TimingTaskManager().task_failed(task)
                del task
                continue
            self._parsing(task, cls)

    def _parsing(self, task, cls):
        try:
            if task.s_cache and len(task.s_cache):
                ret = cls(task, task.s_cache)
            else:
                log.warning('[%s:%s:%s] Fetched Data Error.' % (
                    task.s_platform, task.s_id, task.s_url)
                )
                task.i_state = TimingTaskStatus.ParsedFailed
                TimingTaskManager().task_failed(task)
                del task
                return
        except Exception as e:
            log.exception(e)
            task.i_state = TimingTaskStatus.ParsedFailed
            TimingTaskManager().task_failed(task)
            del task
            return
        if ret.items:
            Storager().storage_to_mongo(ret.db, ret.table, ret.items)
        if ret.tasks:
            self._push_new_task(task, ret.tasks)
        task.i_state = TimingTaskStatus.ParsedSuccess
        TimingTaskManager().task_success(task, True)
        del task

    def _push_new_task(self, task, tasks):
        if not len(tasks):
            return
        for new_task in tasks:
            key = '{base}:{platform}:{task_id}'.format(
                base=self.task_conf.record_key,
                platform=new_task.s_platform,
                task_id=new_task.s_id
            )
            RedisEx().hmset(key, new_task.to_dict())
            TimingTaskManager().push_task(new_task)
        log.debug('[{}:{}] Generate {} New Task.'.format(
            task.s_platform, task.s_id, len(tasks))
        )
