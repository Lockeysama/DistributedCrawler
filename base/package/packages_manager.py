# -*- coding: utf-8 -*-
'''
Created on 2017年4月20日

@author: chenyitao
'''

import importlib
import json
import os

from ..event.event import EventCenter
from ..storage.storager_base import StoragerBase
from common import TDDCLogging
from common.models import PackageModel
from conf import ParserSite


class FetchServer(StoragerBase):
    
    def __init__(self):
        TDDCLogging.info('>Fetch Event Info.<')
        super(FetchServer, self).__init__(push=False)
        TDDCLogging.info('>Fetch Event Info.<')


class PackagesManager(object):
    '''
    classdocs
    '''

    EVENT_TYPE = None

    CONF_PATH = None
    
    PACKAGE_PATH = None

    def __init__(self):
        '''
        Constructor
        '''
        TDDCLogging.info('--->Models Manager Is Starting.')
        self._rules_moulds = {}
        self._load_local_models()
        EventCenter().register(self.EVENT_TYPE,
                               self._models_update_event)
        TDDCLogging.info('--->Models Manager Was Ready.')

    def _load_local_models(self):
        self._rules_moulds = {}
        indexs = [conf for conf in os.listdir(self.CONF_PATH) if conf[-5:] == '.json']
        for index in indexs:
            path = self.CONF_PATH + index
            with open(path, 'r') as f:
                pr = PackageModel(**json.loads(f.read()))
            for model_info in pr.packages:
                self._load_moulds(pr.platform, model_info)

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
            success, ret = FetchServer().pull_once(ParserSite.PLATFORM_CONF_TABLE,
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
        rules_path_base = 'worker.parser.parser_moulds'
        module = importlib.import_module('%s.%s.%s' % (rules_path_base,
                                                       platform,
                                                       model_info.package))
        if not module:
            return
        self._update_models_table(platform, model_info.moulds, module)

    def _update_models_table(self, platform, moulds, module):
        for mould in moulds:
            cls = getattr(module, mould)
            if not cls:
                continue
            feature = cls.__dict__.get('feature', None)
            if not feature:
                continue
            if not self._rules_moulds.get(platform, None):
                self._rules_moulds[platform] = {}
            self._rules_moulds[platform][feature] = cls

    def get_parse_model(self, platform, feature):
        models = self._rules_moulds.get(platform)
        if not models:
            return None
        return models.get(feature)

