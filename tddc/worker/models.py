# encoding: utf-8
"""
@version: ??
@author: chenyitao
@license: Apache Licence 
@software: PyCharm
@file: models.py
@time: 2018/3/27 09:49
"""
import copy
import logging

from sqlalchemy import Column, Integer, String, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from tddc.config.config import CurrentConfig

logging.getLogger('sqlalchemy').setLevel(logging.WARN)


Base = declarative_base()

"""
程序配置ORM Model
"""


class ServerInfoModel(Base):
    __tablename__ = 'server_info'

    id = Column(Integer, primary_key=True)
    name = Column(String(32))
    host = Column(String(32))
    port = Column(Integer)
    username = Column(String(32))
    passwd = Column(String(32))


class RedisModel(Base):
    """
    Redis服务配置
    """
    __tablename__ = 'redis_info'

    id = Column(Integer, primary_key=True)
    name = Column(String(32))
    host = Column(String(32))
    port = Column(Integer)
    username = Column(String(32))
    passwd = Column(String(32))


class MySQLModel(Base):
    """
    Redis服务配置
    """
    __tablename__ = 'mysql_info'

    id = Column(Integer, primary_key=True)
    name = Column(String(32))
    host = Column(String(32))
    port = Column(Integer)
    username = Column(String(32))
    passwd = Column(String(32))
    db = Column(String(32))


class HBaseModel(Base):
    """
    HBase 服务配置
    """
    __tablename__ = 'hbase_info'

    id = Column(Integer, primary_key=True)
    name = Column(String(32))
    host = Column(String(32))
    port = Column(Integer)
    username = Column(String(32))
    passwd = Column(String(32))


class KafkaModel(Base):
    """
    Kafka 服务配置
    """
    __tablename__ = 'kafka_info'

    id = Column(Integer, primary_key=True)
    name = Column(String(32))
    host = Column(String(32))
    port = Column(Integer)
    username = Column(String(32))
    passwd = Column(String(32))


class MongoModel(Base):
    """
    MongoDB 服务配置
    """
    __tablename__ = 'mongo_info'

    id = Column(Integer, primary_key=True)
    name = Column(String(32))
    host = Column(String(32))
    port = Column(Integer)
    username = Column(String(32))
    passwd = Column(String(32))


class WorkerModel(Base):
    """
    Worker 配置：platform：[crawler | parser | proxy | ...]
    """
    __tablename__ = 'worker_info'

    id = Column(Integer, primary_key=True)
    name = Column(String(32))
    platform = Column(String(32))
    feature = Column(String(32))


class EventModel(Base):
    """
    事件中心配置
    """
    __tablename__ = 'event_info'

    id = Column(Integer, primary_key=True)
    topic = Column(String(32))
    record_key_base = Column(String(64))
    status_key_base = Column(String(64))


class ModulesModel(Base):
    """
    扩展模块信息
    """
    __tablename__ = 'extra_modules'

    id = Column(Integer, primary_key=True)
    own = Column(String(16))
    platform = Column(String(32))
    feature = Column(String(32))
    package = Column(String(64))
    mould = Column(String(32))
    url = Column(String(1024))
    version = Column(String(16))
    file_md5 = Column(String(32))
    valid = Column(Boolean, default=True)
    timestamp = Column(Integer)

    def update(self, new_modules):
        self.own = new_modules.own
        self.platform = new_modules.platform
        self.feature = new_modules.feature
        self.package = new_modules.package
        self.mould = new_modules.mould
        self.url = new_modules.url
        self.version = new_modules.version
        self.file_md5 = new_modules.file_md5
        self.valid = new_modules.valid
        self.timestamp = new_modules.timestamp

    def to_dict(self):
        kws = copy.deepcopy(self.__dict__)
        del kws['_sa_instance_state']
        return kws


class TaskConfigModel(Base):
    """
    任务管理配置
    """
    __tablename__ = 'task_config'

    id = Column(Integer, primary_key=True)
    crawler_topic = Column(String(32))
    parser_topic = Column(String(32))
    cache_key_base = Column(String(32))
    status_key_base = Column(String(32))
    record_key_base = Column(String(32))
    max_queue_size = Column(Integer)


engine = create_engine(CurrentConfig.SQLALCHEMY_DATABASE_URI)
Base.metadata.create_all(engine)
DBSession = sessionmaker(bind=engine)()
