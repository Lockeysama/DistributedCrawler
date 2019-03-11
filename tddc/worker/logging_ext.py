# -*- coding: utf-8 -*-
"""
@author  : chenyitao
@email   : yt.chen@bshier.com
@license: Apache Licence
@software: PyCharm
@file    : logging_ext.py
@time    : 2018/9/10 12:01
"""
import logging
import sys

from ..base.util import Device
from ..default_config import default_config

from .event import EventCenter
from .redisex import RedisEx
from .define.event import LogOnlineSwitch
from .models.event_model import Event


"""
日志 ONLINE
    True: 输出到Redis(Publish)
    False: 只输出本地文件
"""
ONLINE = {
    logging.DEBUG: False,
    logging.INFO: False,
    logging.WARNING: False,
    logging.ERROR: False,
    logging.CRITICAL: False
}


def log_record_str(self):
    return '{}'.format({
        'lv_name': self.levelname,
        'path': self.pathname,
        'line': self.lineno,
        'name': self.name,
        'func': self.funcName,
        'msg': self.msg,
        'date': self.asctime,
        'wf': default_config.FEATURE,
        'wp': default_config.PLATFORM,
        'ip': Device.mac()
    })


if sys.version > '3':
    def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=False):
        sinfo = None
        if logging._srcfile:
            # IronPython doesn't track Python frames, so findCaller raises an
            # exception on some versions of IronPython. We trap it here so that
            # IronPython can use logging.
            try:
                fn, lno, func, sinfo = self.findCaller(stack_info)
            except ValueError:  # pragma: no cover
                fn, lno, func = "(unknown file)", 0, "(unknown function)"
        else:  # pragma: no cover
            fn, lno, func = "(unknown file)", 0, "(unknown function)"
        if exc_info:
            if isinstance(exc_info, BaseException):
                exc_info = (type(exc_info), exc_info, exc_info.__traceback__)
            elif not isinstance(exc_info, tuple):
                exc_info = sys.exc_info()
        record = self.makeRecord(self.name, level, fn, lno, msg, args,
                                 exc_info, func, extra, sinfo)
        self.handle(record)
        return record
else:
    def _log(self, level, msg, args, exc_info=None, extra=None):
        """
        Low-level logging routine which creates a LogRecord and then calls
        all the handlers of this logger to handle the record.
        """
        if logging._srcfile:
            # IronPython doesn't track Python frames, so findCaller raises an
            # exception on some versions of IronPython. We trap it here so that
            # IronPython can use logging.
            try:
                fn, lno, func = self.findCaller()
            except ValueError as e:
                fn, lno, func = "(unknown file)", 0, "(unknown function)"
        else:
            fn, lno, func = "(unknown file)", 0, "(unknown function)"
        if exc_info:
            if not isinstance(exc_info, tuple):
                exc_info = sys.exc_info()
        record = self.makeRecord(self.name, level, fn, lno, msg, args, exc_info, func, extra)
        self.handle(record)
        return record


def debug(self, msg, *args, **kwargs):
    """
    Log 'msg % args' with severity 'DEBUG'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.debug("Houston, we have a %s", "thorny problem", exc_info=1)
    """
    if self.isEnabledFor(logging.DEBUG):
        record = self._log(logging.DEBUG, msg, args, **kwargs)
        if ONLINE.get(logging.DEBUG):
            RedisEx().publish(
                'tddc:log:{}'.format(default_config.PLATFORM.lower()),
                '{}==>{}'.format(default_config.FEATURE, record)
            )


def info(self, msg, *args, **kwargs):
    """
    Log 'msg % args' with severity 'INFO'.

    To pass exception information, use the keyword argument exc_info with
    a true value, e.g.

    logger.info("Houston, we have a %s", "interesting problem", exc_info=1)
    """
    if self.isEnabledFor(logging.INFO):
        record = self._log(logging.INFO, msg, args, **kwargs)
        if ONLINE.get(logging.INFO):
            RedisEx().publish(
                'tddc:log:{}'.format(default_config.PLATFORM.lower()),
                '{}==>{}'.format(default_config.FEATURE, record)
            )


def warning(self, msg, *args, **kwargs):
    """
    Log 'msg % args' with severity 'WARNING'.

    To pass exception information, use the keyword argument exc_info with
    a true value, e.g.

    logger.warning("Houston, we have a %s", "bit of a problem", exc_info=1)
    """
    if self.isEnabledFor(logging.WARNING):
        record = self._log(logging.WARNING, msg, args, **kwargs)
        if ONLINE.get(logging.WARNING):
            RedisEx().publish(
                'tddc:log:{}'.format(default_config.PLATFORM.lower()),
                '{}==>{}'.format(default_config.FEATURE, record)
            )


def error(self, msg, *args, **kwargs):
    """
    Log 'msg % args' with severity 'ERROR'.

    To pass exception information, use the keyword argument exc_info with
    a true value, e.g.

    logger.error("Houston, we have a %s", "major problem", exc_info=1)
    """
    if self.isEnabledFor(logging.ERROR):
        record = self._log(logging.ERROR, msg, args, **kwargs)
        if ONLINE.get(logging.ERROR):
            RedisEx().publish(
                'tddc:log:{}'.format(default_config.PLATFORM.lower()),
                '{}==>{}'.format(default_config.FEATURE, record)
            )


def critical(self, msg, *args, **kwargs):
    """
    Log 'msg % args' with severity 'CRITICAL'.

    To pass exception information, use the keyword argument exc_info with
    a true value, e.g.

    logger.critical("Houston, we have a %s", "major disaster", exc_info=1)
    """
    if self.isEnabledFor(logging.CRITICAL):
        record = self._log(logging.CRITICAL, msg, args, **kwargs)
        if ONLINE.get(logging.CRITICAL):
            RedisEx().publish(
                'tddc:log:{}'.format(default_config.PLATFORM.lower()),
                '{}==>{}'.format(default_config.FEATURE, record)
            )


def online_print_switch(event):
    if event.e_type != LogOnlineSwitch:
        return
    lv = event.event.get('lv')
    activate = event.event.get('activate')
    global ONLINE
    ONLINE[lv] = activate
    EventCenter().update_the_status(event, Event.Status.Executed_Success)


def patch():
    EventCenter._dispatcher[LogOnlineSwitch] = online_print_switch
    logging.LogRecord.__str__ = log_record_str
    logging.Logger._log = _log
    logging.Logger.debug = debug
    logging.Logger.info = info
    logging.Logger.warning = warning
    logging.Logger.warn = warning
    logging.Logger.error = error
    logging.Logger.critical = critical
    logging.Logger.fatal = critical
