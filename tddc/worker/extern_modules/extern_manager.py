# -*- coding: utf-8 -*-
'''
Created on 2017年4月20日

@author: chenyitao
'''

import importlib
import json
import os

from tddc import TDDCLogger, Singleton
from tddc.config.config_center import ConfigCenter


class ExternManager(TDDCLogger):
    '''
    classdocs
    '''
    __metaclass__ = Singleton

    def __init__(self):
        super(ExternManager, self).__init__()
        self._start()

    def _start(self):
        '''
        Constructor
        '''
        self.info('Extern Modules Is Loading.')
        self._load_local_models()
        self.info('Extern Modules Was Loaded.')

    def _load_local_models(self):
        self._rules_moulds = {}
        conf = ConfigCenter().get_extern_modules()
        if not conf:
            return
        for platform, packages in conf.items():
            for package in packages:
                try:
                    self._load_moulds(package)
                except Exception as e:
                    self.exception(e)

    def _models_update_event(self, event):
        successe, ret = FetchServer(self.site).pull_once(event.event.table,
                                                         event.event.platform,
                                                         'modules',
                                                         'index')
        if not successe:
            TDDCLogging.error('Module Update Failed.\n' + event.to_json())
            return
        status = self._update(event, ret[0])
        EventCenter().update_status('tddc.event.status.%s' % event.event.table.split('_')[-1],
                                    event.id,
                                    str(status))

    def create_package(self, package):
        path = './worker/extern_modules/%s/' % package
        if not os.path.exists(path):
            os.mkdir(path)
            with open(path+'__init__.py', 'a') as _:
                self.logger.info('Make New Rules Package Success.')

    def _download_moulds(self, platform, update_list, event):
        for model_info in update_list:
            success, ret = FetchServer(self.site).pull_once(event.event.table,
                                                            platform,
                                                            'modules',
                                                            model_info.package)
            if not success or not ret:
                TDDCLogging.warning('Rules Fetch Exception.')
                return False
            self.create_package(platform)
            file_path = ('./worker/extern_modules/' 
                         + platform + '/' 
                         + model_info.package)
            if os.path.exists(file_path + '.py'):
                os.remove(file_path + '.py')
            if os.path.exists(file_path + '.pyc'):
                os.remove(file_path + '.pyc')
            with open(file_path + '.py', 'a') as f:
                f.write(ret[0])
        return True

    @staticmethod
    def update_check(local_packages, remote_packages):
        update_list = []
        for remote_package in remote_packages:
            if not local_packages:
                update_list.append(remote_package)
                continue
            local_package = local_packages.get(remote_package.feature)
            if (remote_package.feature == local_package.feature and 
                int(remote_package.version) > int(local_package.version)):
                update_list.append(remote_package)
        return update_list

    def _update(self, event, models_info):
        '''
        return 0: 不需更新 1：更新成功 -1：更新失败
        '''
        remote_pr = PackageModel(**{'platform': event.event.platform,
                                    'packages': json.loads(models_info)})
        local_packages = self._rules_moulds.get(remote_pr.platform)
        update_list = self.update_check(local_packages, remote_pr.packages)
        if not len(update_list):
            return 0
        if not self._download_moulds(remote_pr.platform, update_list, event):
            return -1
        self._cf.update_extern_modules_conf(remote_pr.platform, update_list)
        if not self._reload_models(remote_pr.platform, update_list):
            return -1
        return 1

    def _reload_models(self, platform, update_list):
        for model_info in update_list:
            if not self._load_moulds(platform, model_info):
                return False
        return True

    def _load_moulds(self, package):
        rules_path_base = 'worker.extern_modules'
        try:
            module = importlib.import_module('%s.%s.%s' % (rules_path_base,
                                                           package.platform,
                                                           package.package))
        except Exception as e:
            self.exception(e)
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

    def get_model(self, platform, feature):
        models = self._rules_moulds.get(platform)
        if not models:
            return None
        return models.get(feature)

    def get_all_modules(self):
        return self._rules_moulds
