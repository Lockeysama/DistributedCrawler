# -*- coding: utf-8 -*-
'''
Created on 2017年4月20日

@author: chenyitao
'''

import importlib
import json
import logging
import os

from ...util.util import Singleton

from ..models import DBSession, ModulesModel
from ..event import EventType, EventCenter, EventStatus
from ..storager import Storager

log = logging.getLogger(__name__)


class ExternManager(object):
    '''
    classdocs
    '''
    __metaclass__ = Singleton

    def __init__(self):
        log.info('Extern Modules Is Loading.')
        super(ExternManager, self).__init__()
        EventCenter()
        Storager()
        self._load_local_models()
        log.info('Extern Modules Was Loaded.')

    def _load_local_models(self):
        self._rules_moulds = {}
        conf = DBSession.query(ModulesModel).all()
        if not conf:
            return False
        for module_info in conf:
            try:
                self._load_moulds(module_info)
            except Exception as e:
                log.exception(e)
                return False
        return True

    @staticmethod
    @EventCenter.route(EventType.ExternModuleUpdate)
    def _models_update_event(event):
        EventCenter().update_the_status(event,
                                        EventStatus.Executed_Success
                                        if ExternManager()._update(event)
                                        else EventStatus.Executed_Failed)

    def _get_remote_config(self, platform):
        success, config = Storager().hbase.get(self.config.config_table,
                                               platform,
                                               'config',
                                               'config')
        return json.loads(config.get('config:config')) if success else None

    def _create_package(self, path, platform):
        if not os.path.exists(path):
            os.mkdir(path)
            with open(path + '__init__.py', 'a') as _:
                log.info('Create %s Extern Modules Packages.' % platform)

    def _download_package_file(self, platform, remote_config, path):
        for feature, package in remote_config.items():
            package_package = package.get('package')
            success, package_content = Storager().hbase.get(self.config.config_table,
                                                            platform,
                                                            'content',
                                                            package_package)
            if not success:
                return False
            path_base = '%s/%s/' % (path, platform)
            self._create_package(path_base, platform)
            with open(path_base + package.get('package') + '.py', 'w') as f:
                f.write(package_content.get('content:' + package_package))
        return True

    def _update(self, event):
        log.info('Extern Modules Is Updating...')
        platform = event.event.get('platform')
        if not platform:
            return False
        remote_config = self._get_remote_config(platform)
        if not remote_config:
            return False
        path = os.popen('find . -name extern_modules').readlines()[0].strip()
        if not self._download_package_file(platform, remote_config, path):
            return False
        local_config = [type('PackageInfo', (), config) for _, config in remote_config.items()]
        if not WorkerConfigCenter().set_extern_modules(platform, local_config):
            return False
        if not self._load_local_models():
            return False
        log.info('Extern Modules Was Updated.')
        return True

    def _load_moulds(self, package):
        rules_path_base = 'worker.extern_modules'
        try:
            path = '%s.%s.%s' % (rules_path_base, package.platform, package.package)
            pyc_path = path.replace('.', '/') + '.pyc'
            if os.path.exists(pyc_path):
                os.remove(pyc_path)
            module = importlib.import_module(path)
            module = reload(module)
        except Exception as e:
            log.exception(e)
            return False
        if not module:
            return False
        if not self._update_models_table(package.platform, package.mould, module):
            return False
        return True

    def _update_models_table(self, platform, mould, module):
        cls = getattr(module, mould)
        if not cls:
            return False
        feature = cls.__dict__.get('feature', None)
        if not feature:
            return False
        if not self._rules_moulds.get(platform, None):
            self._rules_moulds[platform] = {}
        self._rules_moulds[platform][feature] = cls
        return True

    def get_model(self, platform, feature=None):
        models = self._rules_moulds.get(platform)
        if not models:
            return None
        return models.get(feature) if feature else models

    def get_all_modules(self):
        return self._rules_moulds
