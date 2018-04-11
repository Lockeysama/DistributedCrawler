# encoding: utf-8
"""
@version: ??
@author: chenyitao
@license: Apache Licence 
@software: PyCharm
@file: config.py
@time: 2018/3/28 13:36
"""
import os

basedir = os.path.abspath('./')


class Config(object):
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

    SQLALCHEMY_TRACK_MODIFICATIONS = True


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
                             'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'data.sqlite')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}


CurrentConfig = config['default']
# CurrentConfig = config['testing']
# CurrentConfig = config['production']


def register_config_cls(config_type, cls):
    """
    注册自定义配置文件
    :param config_type: config的key
    :param cls: 配置类，config的value
    """
    config[config_type] = cls


def switch_config(config_type):
    """
    切换配置
    :param config_type:
    """
    global CurrentConfig
    CurrentConfig = config.get(config_type)
