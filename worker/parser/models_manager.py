# -*- coding: utf-8 -*-
'''
Created on 2017年4月12日

@author: chenyitao
'''

import os
import json
import gevent
import importlib

from log import TDDCLogging
from conf import ParserSite
from common.models.events.event_base import EventType
from common.models.rules.parser import ParserRules
from worker.parser.storager import ParseStorager
from worker.parser.event import ParserEventCenter


class ParseModelsManager(object):
    '''
    classdocs
    '''

    local_conf_path_base = './conf/parse_rule_index/'

    def __init__(self):
        '''
        Constructor
        '''
        TDDCLogging.info('-->Parser Models Manager Is Starting.')
        self._rules_moulds = {}
        self._load_local_models()
        ParserEventCenter().register(EventType.Parser.MODULE, self._models_update_event)
        TDDCLogging.info('-->Parser Models Manager Was Ready.')
    
    def _load_local_models(self):
        self._rules_moulds = {}
        indexs = os.listdir(self.local_conf_path_base)
        for index in indexs:
            path = self.local_conf_path_base + index
            with open(path, 'r') as f:
                pr = ParserRules(**json.loads(f.read()))
            for model_info in pr.models:
                self._load_moulds(pr.platform, model_info)
    
    def _models_update_event(self, event):
        successe, ret = ParseStorager().pull_once(event.table,
                                                  event.platform,
                                                  'models',
                                                  'index')
        if not successe:
            return
        self._update(event, ret[0])

    @staticmethod
    def get_local_conf(platform):
        _conf_path = ParseModelsManager.local_conf_path_base + platform + '.json' 
        if os.path.exists(_conf_path):
            with open(_conf_path, 'r') as f:
                return json.loads(f.read())
        return {}
    
    @staticmethod
    def save_local_conf(remote_pr):
        conf_path = ParseModelsManager.local_conf_path_base + remote_pr.platform + '.json'
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
            success, ret = ParseStorager().pull_once(ParserSite.PLATFORM_CONF_TABLE,
                                                     platform,
                                                     'models',
                                                     model_info.package)
            if not success or not ret:
                print('Rules Fetch Exception.')
            self.create_package(platform)
            file_path = ('./worker/parser/parser_moulds/' 
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
        for remote_model_info in remote_pr.models:
            for local_model_info in local_pr.models:
                if (remote_model_info.package == local_model_info.package and 
                    int(remote_model_info.version) > int(local_model_info.version)):
                    update_list.append(remote_model_info)
        return update_list

    def _update(self, event, models_info):
        remote_pr = ParserRules(**json.loads(models_info))
        local_pr = ParserRules(**self.get_local_conf(remote_pr.platform))
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


def main():
    ParseModelsManager()
    while True:
        gevent.sleep()

if __name__ == '__main__':
    main()