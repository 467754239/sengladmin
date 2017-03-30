#!/usr/bin/python
# -*- coding:utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
# copyright 2016 Wshuai, Inc.
# All Rights Reserved.

# @author: WShuai Inc.

import os
import shutil
import tarfile
import hashlib

from django.conf import settings

from commAws import S3Handler
from commYaml import YamlHandler
from commConfig import ConfigHandler
from commInception import InceptionHandler
from sengladmin.models import Datacenter,DeployGroup,Service,Health,Config,Package,Q

class ServicePackage(object):
    def __init__(self, service, version, region, file_path, tar_file, md5, env, LOG = None):
        self.service = service
        self.version = version
        self.region = region
        self.file_path = file_path
        self.tar_file = tar_file
        self.md5 = md5
        self.env = env
        self.LOG = LOG
        self.new_md5 = None
        self.uncompress_path = os.path.join('/tmp', service, version)
        self.md5_status = 'pass'
        self.sql_status = 'pass'
        self.endpoint_status = 'pass'
        self.config_status = 'pass'
        self.inception_handler = InceptionHandler(settings.INCEPTION_HOST, settings.INCEPTION_PORT, LOG = self.LOG)
        self.release_note = None
        return
    
    def compute_md5(self):
        if not os.path.isfile(self.tar_file):
            return
        hash_md5 = hashlib.md5()
        file_object = file(self.tar_file,'rb')
        while True:
            content = file_object.read(8096)
            if not content:
                break
            hash_md5.update(content)
        file_object.close()
        return hash_md5.hexdigest()

    def compress(self):
        basedir = os.getcwd()
        os.chdir(self.uncompress_path)
        tar_file = os.path.join(self.uncompress_path, '{0}.tar.gz'.format(self.service))

        os.system('tar -zcf {0} *'.format(tar_file))
        #with tarfile.open(tar_file, 'w:gz') as file_handler:
        #    for root, dir, files in os.walk('.'):
        #        if not dir and not files:
        #            file_handler.add(root)
        #        for file in files:
        #            file_handler.add(os.path.join(root, file))
        os.chdir(basedir)
        return
    
    def uncompress(self):
        if not os.path.isfile(self.tar_file):
            return
        file_object = tarfile.open(self.tar_file)
        file_object.extractall(path = self.uncompress_path)
        file_object.close()
        return

    def get_all_database(self):
        database_configs = []
        datacenters = Datacenter.objects()
        for datacenter in datacenters:
            database_config = {}
            configs = Config.objects(key = 'MYSQL_ADDR', domain = 'GLOBAL', datacenter = datacenter.name)
            if configs:
                database_config['mysql_addr'] = configs[0].value
            configs = Config.objects(key = 'MYSQL_PORT', domain = 'GLOBAL', datacenter = datacenter.name)
            if configs:
                database_config['mysql_port'] = configs[0].value
            configs = Config.objects(key = 'MYSQL_USER', domain = 'GLOBAL', datacenter = datacenter.name)
            if configs:
                database_config['mysql_user'] = configs[0].value
            configs = Config.objects(key = 'MYSQL_PWD', domain = 'GLOBAL', datacenter = datacenter.name)
            if configs:
                database_config['mysql_pwd'] = configs[0].value
            database_config['datacenter'] = datacenter.name
            database_configs.append(database_config)
        return database_configs

    def auto_create_health(self, group_name):
        health_file = os.path.join(self.uncompress_path, 'healthcheck', 'healthcheck.yml')
        self.yaml_handler = YamlHandler(health_file, LOG = self.LOG)
        if not self.yaml_handler.load():
            return False

        groups = DeployGroup.objects(name = group_name)
        group = groups[0]

        want_healths = self.yaml_handler.process_health()
        for want_health in want_healths:
            want_health['associate'] = True
 
            if not group.healthchecks:
                group.healthchecks = [want_health['name']]
            elif want_health['name'] not in group.healthchecks:
                group.healthchecks.append(want_health['name'])
            
            healths = Health.objects(name = want_health['name'])
            if not healths:
                health = Health(
                    name = want_health['name'],
                    type = want_health['type'],
                    value = want_health['value'],
                    interval = want_health['interval'],
                    timeout = want_health['timeout'],
                    pending = want_health['pending'],
                    healthy_threshold = want_health['healthy_threshold'],
                    unhealthy_threshold = want_health['unhealthy_threshold'],
                    failback = want_health['failback'],
                    associate = True,
                    groups = [group_name]
                )
            else:
                health = healths[0]
                health.type = want_health['type']
                health.value = want_health['value']
                health.interval = want_health['interval']
                health.timeout = want_health['timeout']
                health.pending = want_health['pending']
                health.healthy_threshold = want_health['healthy_threshold']
                health.unhealthy_threshold = want_health['unhealthy_threshold']
                health.failback = want_health['failback']
                health.associate = True
                if not health.groups:
                    health.groups = [group_name]
                elif group_name not in health.groups:
                    health.groups.append(group_name)
            health.save()
        group.save()
        return want_healths

    def audit_datacenter_sql(self, sql_file, database_configs):
        sql_str = None
        try:
            with open(sql_file) as file_handler:
                sql_str = file_handler.read()
        except Exception as e:
            self.LOG.error('Unkown exception: {0}'.format(e))

        database_name = None
        if sql_str.find('USE ') < 0:
            if sql_str.find('use ') > 0:
                database_name = sql_str[sql_str.find('use ') + 4 : sql_str.index(';', sql_str.find('use '))]
        else:
            database_name = sql_str[sql_str.find('USE ') + 4 : sql_str.index(';', sql_str.find('USE '))]
        self.LOG.debug('database_name is {0}'.format(database_name))
        if not database_name:
            return False

        for database_config in database_configs:
            if 'mysql_addr' in database_config.keys() and \
                'mysql_port' in database_config.keys() and \
                'mysql_user' in database_config.keys() and \
                'mysql_pwd' in database_config.keys():
                if self.inception_handler.audit(
                    sql_str,
                    database_config['mysql_addr'],
                    database_config['mysql_port'],
                    database_config['mysql_user'],
                    database_config['mysql_pwd'],
                    database_name
                ):
                    return True
                else:
                    continue
        return False
        
    def audit_md5(self):
        if self.compute_md5() == self.md5:
            return True
        else:
            self.md5_status = 'refuse'
            return False
    
    def audit_sql(self):
        self.sql_status = 'pass'
        return 
        '''
        sql_path = os.path.join(self.uncompress_path, 'sql')
        result = os.walk(sql_path)
        ret = True
        for path, dirs, files in result:
            if not files:
                ret = True
            else:
                for file in files:
                    source_file_path = os.path.join(sql_path, file)
                    file_name = file.replace('.sql', '.%s.sql' % self.version)
                    save_file_path = os.path.join(settings.SQL_SAVE_PATH, self.service, file_name)
                    path_name = os.path.dirname(save_file_path)
                    if not os.path.exists(path_name):
                        os.makedirs(path_name)
                    shutil.copyfile(source_file_path, save_file_path)
                    
                    database_configs = self.get_all_database()
                    if self.audit_datacenter_sql(source_file_path, database_configs):
                        continue
                    else:
                        ret = False
                        break
            break
        if ret:
            self.sql_status = 'pass'    
        else:
            self.sql_status = 'refuse'
        return
        '''
    
    def audit_port(self):
        if self.service == 'agent':
            self.endpoint_status = 'pass'
            return

        port_file = os.path.join(self.uncompress_path, 'endpoint', 'endpoint.yml')
        self.yaml_handler = YamlHandler(port_file, LOG = self.LOG)
        if not self.yaml_handler.load():
            self.endpoint_status = 'refuse'
            return
        want_endpoint = self.yaml_handler.process_endpoint()

        service_objects = Service.objects(name = self.service)
        service_object = service_objects[0]
        exist_endpoint = {}
        for service_endpoint in service_object.endpoints:
            exist_endpoint[service_endpoint['port']] = service_endpoint['type']
    
        for port in want_endpoint.keys():
            if port not in exist_endpoint.keys():
                self.endpoint_status = 'waiting'
                break
            else:
                if want_endpoint[port] != exist_endpoint[port]:
                    self.endpoint_status = 'waiting'
                    break
                else:
                    continue

        packages = Package.objects(service = self.service, version = self.version)
        package = packages[0]
        if self.endpoint_status == 'waiting':
            if not package.audit:
                package.audit = {'port': [item[1] + ':' + str(item[0]) for item in want_endpoint.items()]}
            else:
                package.audit['port'] = [item[1] + ':' + str(tem[0]) for item in want_endpoint.items()]
        self.LOG.debug('audit port, audit is {0}'.format(package.audit))
        #else:
        #    if package.audit:
        #        if 'config' in package.audit.keys():
        #            if not package.audit['config']:
        #                package.audit = {}
        #            else:
        #                package.audit['port'] = None
        #        else:
        #            package.audit = {}
        package.save()
        return

    def pass_port(self):
        port_file = os.path.join(self.uncompress_path, 'endpoint', 'endpoint.yml')
        self.yaml_handler = YamlHandler(port_file, LOG = self.LOG)
        if not self.yaml_handler.load():
            self.endpoint_status = 'refuse'
            return
        service_objects = Service.objects(name = self.service)
        if not service_objects:
            return
        service_object = service_objects[0]
        service_object.endpoints = self.yaml_handler.yaml_content['exec']
        service_object.save()

        packages = Package.objects(service = self.service, version = self.version)
        package = packages[0]

        #if package.audit:
        #    if 'config' in package.audit.keys():
        #        if not package.audit['config']:
        #            package.audit = {}
        #        else:
        #            package.audit['port'] = None
        #    else:
        #        package.audit = {}

        #package.audit['port'] = None
        package.save()
        return

    def audit_config(self):
        if self.service == 'agent' or self.service == 'work-proxy' or self.service == 'load-balance':
            self.config_status = 'pass'
            return

        exist_config = []
        config_file = os.path.join(self.uncompress_path, 'config', 'sengled.properties.ctmpl')
        config = ConfigHandler()
        if not os.path.isfile(config_file):
            self.config_status = 'refuse'
            return
        config.read(config_file)
        want_keys = config.defaults()
        datacenters = Datacenter.objects()
        add_keys = []
        for datacenter in datacenters:
            config = Config.objects(Q(datacenter = datacenter.name) & (Q(domain = self.service) | Q(domain = 'GLOBAL')))
            exist_keys = [item.key for item in config]
            for key in want_keys:
                if key == 'PUBLIC_IPV4' or key == 'PRIVATE_IPV4':
                    continue
                if key not in exist_keys:
                    add_keys.append(key)
                    continue

        packages = Package.objects(service = self.service, version = self.version)
        package = packages[0]
        add_keys = list(set(add_keys))
        if add_keys:
            self.config_status = 'waiting'
            if not package.audit:
                package.audit = {'config': [key for key in add_keys]}
            else:
                package.audit['config'] = [key for key in add_keys]
        self.LOG.debug('audit config, audit is {0}'.format(package.audit))
        #else:
        #    if package.audit:
        #        if 'port' in package.audit.keys():
        #            if not package.audit['port']:
        #                package.audit = {}
        #            else:
        #                package.audit['config'] = None
        #        else:
        #            package.audit = {}
        package.save()
        return

    def set_package_status(self):
        packages = Package.objects(service = self.service, version = self.version)
        package = packages[0]

        package.status['md5'] = self.md5_status
        package.status['sql'] = self.sql_status
        package.status['port'] = self.endpoint_status
        package.status['config'] = self.config_status

        package.save()
        return

    def clear(self):
        shutil.rmtree(self.uncompress_path)
        return

    def get_release_note(self):
        return self.release_note

    def get_service(self):
        return self.service

    def process_config(self):
        self.LOG.debug('self.region is {0}'.format(self.region))
        datacenters = Datacenter.objects(region = self.region, env = self.env)
        datacenter = datacenters[0]

        self.uncompress()

        # get release not by the way
        if self.service == 'agent':
            release_note_file = os.path.join(self.uncompress_path, 'release_note.txt')
        else:
            release_note_file = os.path.join(self.uncompress_path, 'release_note', 'release_note.txt')
        with open(release_note_file) as file_handler:
            self.release_note = file_handler.read()

        if self.service == 'agent':
            return
 
        config_file = os.path.join(self.uncompress_path, 'config', 'sengled.properties.ctmpl')
        config_handler = ConfigHandler()
        config_handler.read(config_file)
        config_defaults = config_handler.defaults()
        want_keys = [key for key in config_defaults]
        self.LOG.debug('want_keys type is {0} value is {1}'.format(type(want_keys), want_keys))

        config_context_list = ['[DEFAULT]', 'PUBLIC_IPV4=$PUBLIC_IPV4', 'PRIVATE_IPV4=$PRIVATE_IPV4', '']
        configs = Config.objects(Q(datacenter = datacenter.name) & (Q(domain = self.service) | Q(domain = 'GLOBAL'))).order_by('key').order_by('-domain')
        for config in configs:
            if config.key not in want_keys:
                continue
            if config.consul_key:
                config_str = '{0} = {1}'.format(config.key, config.consul_value)
            else:
                config_str = '{0} = {1}'.format(config.key, config.value)
            config_context_list.append(config_str)
            want_keys.remove(config.key)

        for want_key in want_keys:
            if want_key == 'PUBLIC_IPV4' or want_key == 'PRIVATE_IPV4':
                continue
            config_str = '{0} ='.format(want_key)
            config_context_list.append(config_str)

        with open(config_file, 'w') as file_handler:
            file_handler.write('\n'.join(config_context_list))
        self.compress()
        
        s3_handler = S3Handler(self.region, datacenter.agent['access_key_id'], datacenter.agent['secret_access_key'], LOG = self.LOG)
        s3_handler.connect()
        s3_handler.put_file(datacenter.deploy['bucket'], self.file_path, os.path.join(self.uncompress_path, '{0}.tar.gz'.format(self.service)))
        self.LOG.info('xxxxxxxxxxxxxxxxxxxxxxxxx upload s3 finished.')
        with open(os.path.join(self.uncompress_path, '{0}.tar.gz'.format(self.service))) as file_handler:
            md5 = hashlib.md5(file_handler.read()).hexdigest()
            self.new_md5 = md5
        
        self.LOG.debug('new_md5 is {0}'.format(self.new_md5))
        packages = Package.objects(service = self.service, version = self.version)
        package = packages[0]
        package.md5[datacenter.name] = md5
        package.save()

        #self.clear() 
        return

