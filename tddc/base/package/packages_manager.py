# -*- coding: utf-8 -*-
'''
Created on 2017年4月20日

@author: chenyitao
'''

import importlib
import json
import os

from tddc.base.plugins.config_center.config_center import ConfigCenter
from tddc.common.decorator import singleton
from tddc.common.models import PackageModel
from tddc.conf import SiteBase

from ..event.event import TDDCLogging
from ..storage.storager_base import StoragerBase


class FetchServer(StoragerBase):

    def __init__(self):
        TDDCLogging.info('>Fetch Event Info.<')
        super(FetchServer, self).__init__(push=False)
        TDDCLogging.info('>Fetch Event Info.<')


@singleton
class PackagesManager(object):
    '''
    classdocs
    '''

    def start(self, conf_path):
        '''
        Constructor
        '''
        self._conf_path = conf_path
        self._cf = ConfigCenter(self._conf_path)
        TDDCLogging.info('-->Extern Modules Manager Is Starting.')
        self._rules_moulds = {}
        self._load_local_models()
        TDDCLogging.info('-->Extern Modules Manager Was Ready.')

    def _load_local_models(self):
        self._rules_moulds = {}
        conf = self._cf.load_extern_modules_conf()
        for platform, packages in conf.items():
            for package in packages:
                try:
                    self._load_moulds(platform, package)
                except Exception, e:
                    TDDCLogging.error(e)

    def _models_update_event(self, event):
        successe, ret = FetchServer().pull_once(event.table,
                                                event.platform,
                                                'models',
                                                'index')
        if not successe:
            return
        self._update(event, ret[0])

    @classmethod
    def get_local_conf(cls, platform):
        _conf_path = cls.CONF_PATH + platform + '.json'
        if os.path.exists(_conf_path):
            with open(_conf_path, 'r') as f:
                return json.loads(f.read())
        return {}

    @classmethod
    def save_local_conf(cls, remote_pr):
        conf_path = (cls.CONF_PATH 
                     + remote_pr.platform + '.json')
        if os.path.exists(conf_path):
            os.remove(conf_path)
        with open(conf_path, 'a') as f:
            f.write(remote_pr.to_json())

    @staticmethod
    def create_package(package):
        paths = package.split('.')
        path = './'
        for folder in paths[:-1]:
            path += folder + '/'
            if not os.path.exists(path):
                os.mkdir(path)
                with open(path+'__init__.py', 'a') as _:
                    print('Make New Rules Package Success.')

    def _download_moulds(self, platform, update_list):
        for model_info in update_list:
            success, ret = FetchServer().pull_once(SiteBase.PLATFORM_CONF_TABLE,
                                                   platform,
                                                   'models',
                                                   model_info.package)
            if not success or not ret:
                print('Rules Fetch Exception.')
            self.create_package(platform)
            file_path = (self.PACKAGE_PATH  # './worker/parser/parser_moulds/' 
                         + platform + '/' 
                         + model_info.package + '.py')
            if os.path.exists(file_path):
                os.remove(file_path)
            if os.path.exists(file_path + 'c'):
                os.remove(file_path + 'c')
            with open(file_path, 'a') as f:
                f.write(ret[0])

    @staticmethod
    def update_check(local_pr, remote_pr):
        update_list = []
        for remote_package_info in remote_pr.packages:
            if not local_pr:
                update_list.append(remote_package_info)
                continue
            for local_package_info in local_pr.packages:
                if (remote_package_info.package == local_package_info.package and 
                    int(remote_package_info.version) > int(local_package_info.version)):
                    update_list.append(remote_package_info)
        return update_list

    def _update(self, event, models_info):
        remote_pr = PackageModel(**json.loads(models_info))
        local_conf_info = self.get_local_conf(remote_pr.platform)
        local_pr = PackageModel(**local_conf_info) if local_conf_info else None
        update_list = self.update_check(local_pr, remote_pr)
        if not len(update_list):
            return
        self._download_moulds(remote_pr.platform, update_list)
        self.save_local_conf(remote_pr)
        self._reload_models(remote_pr.platform, update_list)

    def _reload_models(self, platform, update_list):
        for model_info in update_list:
            self._load_moulds(platform, model_info)

    def _load_moulds(self, platform, model_info):
        rules_path_base = 'worker.extern_modules'
        module = importlib.import_module('%s.%s.%s' % (rules_path_base,
                                                       platform,
                                                       model_info.get('package')))
        if not module:
            return
        self._update_models_table(platform, model_info.get('mould'), module)

    def _update_models_table(self, platform, mould, module):
        cls = getattr(module, mould)
        if not cls:
            return
        feature = cls.__dict__.get('feature', None)
        if not feature:
            return
        if not self._rules_moulds.get(platform, None):
            self._rules_moulds[platform] = {}
        self._rules_moulds[platform][feature] = cls

    def get_parse_model(self, platform, feature):
        models = self._rules_moulds.get(platform)
        if not models:
            return None
        return models.get(feature)

    def get_all_modules(self):
        return self._rules_moulds
