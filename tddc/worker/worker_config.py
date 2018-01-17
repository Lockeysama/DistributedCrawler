# -*- coding: utf-8 -*-
"""
Created on 2017年8月31日

@author: chenyitao
"""

from ..config.config_center import ConfigCenter


class WorkerConfigCenter(ConfigCenter):

    @staticmethod
    def tables():
        return dict(ConfigCenter.tables(),
                    **{"worker": WorkerConfigCenter.worker_fields(),
                       "service": WorkerConfigCenter.service_fields(),
                       "event": WorkerConfigCenter.event_fields(),
                       "extern_modules": WorkerConfigCenter.extern_modules_fields(),
                       "extern_modules_config": WorkerConfigCenter.extern_modules_config_fields(),
                       'task': WorkerConfigCenter.task_fields()})

    @staticmethod
    def worker_fields():
        worker = {"id": {"field_type": "TEXT",
                         "default_value": "host_id"},
                  "name": {"field_type": "TEXT",
                           "default_value": "tddc_worker_name"},
                  "platform": {"field_type": "TEXT"},
                  "describe": {"field_type": "TEXT",
                               "default_value": ("id: Worker唯一标识 | "
                                                 "name: Worker及进程名")}}
        return worker

    @staticmethod
    def service_fields():
        service = {"server_name": {"field_type": "TEXT",
                                   "default_value": "server_name"},
                   "host": {"field_type": "TEXT",
                            "default_value": "127.0.0.1"},
                   "port": {"field_type": "INTEGER",
                            "default_value": 0},
                   "describe": {"field_type": "TEXT",
                                "default_value": ("server_name:[kafka|redis|hbase|zookeeper|...] | "
                                                  "host: server host | "
                                                  "port: server port")}}
        return service

    @staticmethod
    def event_fields():
        event = {"topic": {"field_type": "TEXT",
                           "default_value": "tddc_event"},
                 "group_id": {"field_type": "TEXT",
                              "default_value": "tddc_event_gN"},
                 "record_table": {"field_type": "TEXT",
                                  "default_value": "tddc:event:record:platform"},
                 "status_table": {"field_type": "TEXT",
                                  "default_value": "tddc:event:status:platform"},
                 "describe": {"field_type": "TEXT",
                              "default_value": ("topic: Event Topic Name | "
                                                "group_id: Event Group Name")}}
        return event

    @staticmethod
    def extern_modules_fields():
        extern_modules = {"platform": {"field_type": "TEXT"},
                          "package": {"field_type": "TEXT"},
                          "mould": {"field_type": "TEXT"},
                          "feature": {"field_type": "TEXT"},
                          "version": {"field_type": "TEXT"},
                          "md5": {"field_type": "TEXT"},
                          "valid": {"field_type": "TEXT"},
                          "update_time": {"field_type": "TEXT"},
                          "describe": {"field_type": "TEXT"}}
        return extern_modules

    @staticmethod
    def extern_modules_config_fields():
        extern_modules = {"config_table": {"field_type": "TEXT",
                                           "default_value": "tddc_extern_modules_"},
                          "describe": {"field_type": "TEXT",
                                       "default_value": "扩展模块HBase表配置"}}
        return extern_modules

    @staticmethod
    def task_fields():
        task = {'consumer_topic': {"field_type": "TEXT"},
                'consumer_group': {"field_type": "TEXT",
                                   "default_value": "tddc_consumer_gN"},
                'producer_topic': {"field_type": "TEXT"},
                'status_key_base': {"field_type": "TEXT",
                                    "default_value": "tddc:task:status"},
                'record_key_base': {"field_type": "TEXT",
                                    "default_value": "tddc:task:record"},
                'local_task_queue_size': {"field_type": "INTEGER",
                                          "default_value": 200},
                "describe": {"field_type": "TEXT",
                             "default_value": ("consumer_topic: TaskManager消费任务Topic | "
                                               "consumer_group: TaskManager消费任务Topic的Group | "
                                               "producer_topic: TaskManager发送新任务Topic | "
                                               "status_key_base: 任务在Redis中的状态基础key | "
                                               "record_key_base: 任务在Redis中的记录基础key | "
                                               "local_task_queue_size: 本地任务拉取数量")}}
        return task

    def get_worker(self):
        return self._get_info('worker')

    def get_kafka(self):
        return self.get_services('kafka')

    def get_redis(self):
        return self.get_services('redis')

    def get_hbase(self):
        return self.get_services('hbase')

    def get_zookeeper(self):
        return self.get_services('zookeeper')

    def get_services(self, server_name=None):
        keys = self.tables().get("service").keys()
        sql = "SELECT %s FROM `service`" % ','.join(keys)
        sql += ";" if not server_name else " WHERE server_name=\"%s\";" % server_name
        return self._get_infos(sql, keys, server_name, 'server_name', 'server_name', 'ServerInfo')

    def get_event(self):
        return self._get_info('event')

    def get_extern_modules_config(self):
        return self._get_info('extern_modules_config')

    def get_extern_modules(self, platform=None):
        keys = self.tables().get("extern_modules").keys()
        sql = "SELECT %s FROM `extern_modules` WHERE valid='%s'" % (','.join(keys), '1')
        sql += ";" if not platform else " AND platform=\"%s\";" % platform
        return self._get_infos(sql, keys, platform, 'platform', 'mould', 'ExternModuleInfo')

    def set_extern_modules(self, platform, packages):
        def _insert(self, platform, package):
            sql_fmt = ("INSERT INTO `extern_modules`"
                       "(`platform`,`package`,`mould`,`feature`,`version`,`md5`,`valid`,`update_time`) "
                       "VALUES (\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",datetime());")
            sql = sql_fmt % (platform,
                             package.package,
                             package.mould,
                             package.feature,
                             package.version,
                             package.md5,
                             package.valid)
            try:
                self._connection.execute(sql)
                self._connection.commit()
            except Exception as e:
                self.exception(e)
                return False
            else:
                return True

        def _update(self, platform, package):
            sql_fmt = ("UPDATE `extern_modules` "
                       "SET `version`=\"%s\", `md5`=\"%s\", `valid`=\"%s\", `update_time`=datetime() "
                       "WHERE `feature`=\"%s\" AND `platform`=\"%s\";")
            sql = sql_fmt % (package.version,
                             package.md5,
                             package.valid,
                             package.feature,
                             platform)
            try:
                self._connection.execute(sql)
                self._connection.commit()
            except Exception as e:
                self.exception(e)
                return False
            else:
                return True

        sql_fmt = "SELECT * FROM `extern_modules` WHERE feature=\"%s\";"
        for package in packages:
            sql = sql_fmt % package.feature
            ret = self._connection.execute(sql)
            if len(ret.fetchall()):
                if not _update(self, platform, package):
                    return False
            else:
                if not _insert(self, platform, package):
                    return False
        return True

    def get_task(self):
        return self._get_info('task')

    def _get_infos(self, sql, keys, index, index_name, record_name_key, name_extern):
        records = self._connection.execute(sql).fetchall()
        conf = {}
        for record in records:
            _platform = record[keys.index(index_name)]
            if not conf.get(_platform):
                conf[_platform] = []
            packages = conf.get(_platform, [])
            obj = type(str(record[keys.index(record_name_key)]) + name_extern,
                       (),
                       {keys[i]: record[i] for i in range(len(keys))})
            packages.append(obj)
        conf = conf if conf else None
        return None if not conf else conf if not index else conf.get(index, None)

    def _get_all(self, table_name, record_name, parent_cls=None):
        keys = self.tables().get(table_name).keys()
        sql = 'SELECT %s FROM `%s` WHERE valid=1;' % (', '.join(keys),
                                                      table_name)
        records = self._connection.execute(sql).fetchall()
        ret = []
        for record in records:
            r = type(record_name,
                     parent_cls if parent_cls else (),
                     {keys[i]: record[i] for i in range(len(keys))})
            ret.append(r)
        return ret if len(ret) else None

