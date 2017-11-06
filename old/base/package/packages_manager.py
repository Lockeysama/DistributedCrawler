# -*- coding: utf-8 -*-
'''
Created on 2017年4月20日

@author: chenyitao
'''

import importlib
import json
import os

from tddc.common.decorator import singleton
from tddc.common.models import PackageModel
from tddc.old.base import ConfigCenter
from tddc.old.base import EventCenter

from old.common.models.packages_model.package_model import ModuleModel
from ..event.event import TDDCLogging
from ..storage.storager_base import StoragerBase


class FetchServer(StoragerBase):

    def __init__(self, site):
        TDDCLogging.info('>HBase Fetch Server Is Starting.<')
        super(FetchServer, self).__init__(site.random_hbase_node(), push=False, pull=True)
        TDDCLogging.info('>HBase Fetch Server Was Ready.<')


@singleton
class PackagesManager(object):
    '''
    classdocs
    '''

    def start(self, conf_path, site):
        '''
        Constructor
        '''
        TDDCLogging.info('-->Extern Modules Manager Is Starting.')
        self.site = site
        self._conf_path = conf_path
        self._cf = ConfigCenter(self._conf_path)
        self._rules_moulds = {}
        self._load_local_models()
        TDDCLogging.info('-->Extern Modules Manager Was Ready.')

    def _load_local_models(self):
        self._rules_moulds = {}
        conf = self._cf.load_extern_modules_conf()
        for platform, packages in conf.items():
            for package in packages:
                try:
                    self._load_moulds(platform,
                                      ModuleModel(**package))
                except Exception, e:
                    TDDCLogging.error(e)

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

    @staticmethod
    def create_package(package):
        path = './worker/extern_modules/%s/' % package
        if not os.path.exists(path):
            os.mkdir(path)
            with open(path+'__init__.py', 'a') as _:
                TDDCLogging.info('Make New Rules Package Success.')

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

    def _load_moulds(self, platform, model_info):
        rules_path_base = 'worker.extern_modules'
        module = importlib.import_module('%s.%s.%s' % (rules_path_base,
                                                       platform,
                                                       model_info.package))
        if not module:
            return False
        if not self._update_models_table(platform, model_info.mould, module):
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
