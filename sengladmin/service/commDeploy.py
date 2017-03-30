#!/usr/bin/python
#-*-coding:utf-8-*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
# copyright 2016 Sengled, Inc.
# All Rights Reserved.

# @author: WShuai, Sengled, Inc.

from django.conf import settings

import os
import json
import time
import math
import commConsul
from sengladmin.models import DeployGroup, Package, DeployRecord, DeployProcess, DatacenterVersion, Q

class DeployHandler(object):
    def __init__(self, deploy_init_attr, LOG = None):
        self.service = deploy_init_attr['service']
        self.version = deploy_init_attr['version']
        self.file_path = deploy_init_attr['file_path']
        self.md5 = deploy_init_attr['md5']
        self.operator = deploy_init_attr['operator']
        self.group = deploy_init_attr['group_name']
        self.deploy_policy_type = deploy_init_attr['deploy_policy_type']
        self.deploy_policy_value = deploy_init_attr['deploy_policy_value']
        self.env = deploy_init_attr['env']
        self.datacenter = deploy_init_attr['datacenter_name']
        self.datacenter_cacert = deploy_init_attr['datacenter_cacert']
        self.datacenter_cakey = deploy_init_attr['datacenter_cakey']
        self.datacenter_domain = deploy_init_attr['datacenter_domain']
        self.datacenter_port = deploy_init_attr['datacenter_port']
        self.LOG = LOG
        self.static_sql_files = []
        self.dynamic_sql_files = []
        self.current_version = None
        self.deploy_id = None
        self.deploy_instances = None
        self.single_deploy_min = None
        self.pendings = []
        self.waitings = []
        self.success = []
        self.faileds = []
        self.single_deploy_timeout = settings.DEPLOY_SINGLE_TIMEOUT
        self.deploy_result = None
        return
    
    def init_current_version(self):
        versions = DatacenterVersion.objects(datacenter = self.datacenter, service = self.service)
        if versions:
            self.LOG.debug('versions is {0}'.format(versions[0].to_json()))
            deploy_records = DeployRecord.objects(
                target_version = versions[0].version,
                datacenter = self.datacenter,
                group = self.group,
                service = self.service,
                result = 'success'
            )
            if deploy_records:
                self.LOG.debug('deploy_record is {0}'.format(deploy_records[0].to_json()))
                self.current_version = versions[0].version
                return True
            else:
                self.current_version = 'v0.0.0'
                return False
        else:
            self.current_version = 'v0.0.0'
            return True
    
    def init_sql(self):
        interval_versions = []
        if self.current_version != self.version:
            packages = Package.objects(
                Q(service = self.service) & 
                Q(version__gt = self.current_version) & 
                Q(version__lte = self.version)
            ).order_by('version')
            interval_versions = [
                package.version 
                for package in packages 
                if package.status 
                and package.status['md5'] == 'pass' 
                and package.status['sql'] == 'pass' 
                and package.status['port'] == 'pass' 
                and package.status['config'] == 'pass'
            ]
        else:
            interval_versions = [self.current_version]
        
        for version in interval_versions:
            static_sql_file = os.path.join(settings.SQL_SAVE_PATH, self.service, 'static.%s.sql' % version)
            if os.path.exists(static_sql_file):
                self.static_sql_files.append(static_sql_file)
            dynamic_sql_file = os.path.join(settings.SQL_SAVE_PATH, self.service, 'dynamic.%s.sql' % version)
            if os.path.exists(dynamic_sql_file):
                self.dynamic_sql_files.append(dynamic_sql_file)
        return

    def init_instances(self):
        consul_handler = commConsul.CommConsul(self.datacenter_cacert, self.datacenter_cakey, LOG = self.LOG)
        consul_handler.connect(self.datacenter_domain, self.datacenter_port)
        self.deploy_instances = consul_handler.get_consul_instances(self.service)
        consul_handler.clear_consul_cert()
        return

    def init_deploy(self):
        if self.deploy_instances:
            self.waitings = self.deploy_instances
        return

    def init(self):
        if not self.init_current_version():
            self.LOG.error('last version deploy failed, not allowed deploy to target version [{0}]'.format(self.version))
            return False
        self.init_sql()
        self.LOG.debug('self static_sql_files is [{0}], self dynamic_sql_files is [{0}]'.format(','.join(self.static_sql_files), ','.join(self.dynamic_sql_files)))
        self.init_instances()
        self.LOG.debug('deploy all instances are [{0}]'.format(','.join(self.deploy_instances)))
        self.init_deploy()
        self.LOG.debug('self.waitings are [{0}]'.format(','.join(self.waitings)))
        return True

    def update_group(self):
        groups = DeployGroup.objects(name = self.group)
        group = groups[0]
        group.version = self.version
        group.save()
        return

    def record_deploy(self):
        now_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        self.deploy_id = '{0}-{1}-{2}-{3}'.format(self.group, self.current_version, self.version, now_time.replace('-', '').replace(' ', '').replace(':', ''))
        
        deploy_records = DeployRecord.objects(deploy_id = self.deploy_id)
        if deploy_records:
            self.deploy_id = '{0}-{1}-{2}-{3}-{4}'.format(self.group, self.current_version, self.version, now_time.replace('-', '').replace(' ', '').replace(':', ''), '01')
        deploy_record = DeployRecord(
            deploy_id = self.deploy_id,
            source_version = self.current_version,
            target_version = self.version,
            start_time = now_time,
            result = 'pending',
            env = self.env,
            datacenter = self.datacenter,
            group = self.group,
            service = self.service,
            operator = self.operator
        )
        deploy_record.save()
        
        versions = DatacenterVersion.objects(datacenter = self.datacenter, service = self.service)
        if not versions:
            version = DatacenterVersion(
                datacenter = self.datacenter,
                service = self.service,
                version = self.version,
                time = now_time
            )
            version.save()
        else:
            version = versions[0]
            version.version = self.version
            version.time = now_time
            version.save()
        return
    
    def get_deploy_result(self):
        if self.success:
            self.deploy_result = 'success'
        else:
            self.deploy_result = 'failed'
        return
        
    def modify_deploy(self):
        deploy_records = DeployRecord.objects(deploy_id = self.deploy_id)
        if deploy_records:
            deploy_record = deploy_records[0]
            deploy_record.end_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            deploy_record.result = self.deploy_result
            deploy_record.save()
        return
        
    def get_single_deploy_min(self):
        if self.deploy_policy_value >= 0:
            try:
                if self.deploy_policy_type == 'num':
                    self.single_deploy_min = self.deploy_policy_value
                elif self.deploy_policy_type == 'percent':
                    rate = self.deploy_policy_value * 0.01
                    if float(self.deploy_instances * rate) <= float(self.deploy_instances / 2):
                        self.single_deploy_min = int(math.ceil(float(self.deploy_instances * rate)))
                    else:
                        self.single_deploy_min = int(math.floor(float(self.deploy_instances * rate)))
                else:
                    self.single_deploy_min = 1
            except:
                self.single_deploy_min = 1
        else:
            self.single_deploy_min = self.deploy_policy_value
        return
        
    def is_exec_sql(self):
        if self.static_sql_files or self.dynamic_sql_files:
            return True
        else:
            return False

    def exec_sql(self):
        return True
    
    def modify_consul_deploy(self, current_version):
        consul_handler = commConsul.CommConsul(self.datacenter_cacert, self.datacenter_cakey, LOG = self.LOG)
        consul_handler.connect(self.datacenter_domain, self.datacenter_port)
        
        consul_key = 'deploy/deployGroup/%s/status' % self.group
        consul_value = json.dumps(
            {
                'service': self.service,
                #'cur_version': self.current_version if self.current_version != 'v0.0.0' else self.version,
                'cur_version': current_version,
                'target_version': self.version,
                'deploy_id': self.deploy_id,
                'file_path': self.file_path,
                'verify': self.md5,
            }
        )
        self.LOG.debug('consul_value is {0}'.format(consul_value))
        consul_handler.put_values(consul_key, consul_value)

        consul_handler.clear_consul_cert()
        return

    def is_continue(self):
        if self.waitings:
            return True
        else:
            return False

    def modify_consul_task(self, target_instance):
        consul_handler = commConsul.CommConsul(self.datacenter_cacert, self.datacenter_cakey, LOG = self.LOG)
        consul_handler.connect(self.datacenter_domain, self.datacenter_port)

        consul_key = 'deploy/task/{0}/{1}'.format(self.deploy_id, target_instance)
        consul_value = json.dumps(
            {
                'target_version': self.version,
                'message': 'your turn' 
            }
        )
        consul_handler.put_values(consul_key, consul_value)

        consul_handler.clear_consul_cert()
        return
        
    def record_process(self, target_instance):
        deploy_process = DeployProcess.objects(deploy_id = self.deploy_id, instance = target_instance)
        if deploy_process:
            return
        else:
            deploy_process = DeployProcess(
                deploy_id = self.deploy_id,
                instance = target_instance,
                result = 'pending',
                start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            )
            deploy_process.save()
        return
       
    def allot_task(self):
        if self.deploy_policy_value >= 0:
            deploy_next_num = len(self.waitings) + len(self.success) - int(self.deploy_policy_value)
            if deploy_next_num >= len(self.waitings):
                self.pendings = self.waitings
                self.waitings = []
            else:
                self.pendings = self.waitings[:deploy_next_num]
                self.waitings = self.waitings[deploy_next_num:]
        else:
            if self.waitings:
                self.pendings = [self.waitings.pop()]
        
        self.LOG.debug('self.pendings are [{0}]'.format(','.join(self.pendings)))
        for instance in self.pendings:
            self.modify_consul_task(instance)
            self.record_process(instance)
        return

    def is_last_process_finish(self):
        is_finish = True
        for instance in self.pendings:
            self.LOG.debug('current deporocess id is [{0}], instance is [{1}]'.format(self.deploy_id, instance))
            deploy_processes = DeployProcess.objects(deploy_id = self.deploy_id, instance = instance)
            if not deploy_processes:
                continue
            else:
                deploy_process = deploy_processes[0]
                if deploy_process.result == 'success':
                    # success
                    self.LOG.info('last process deploy finish, and success')
                    self.pendings.remove(instance)
                    self.success.append(instance)
                    continue
                elif deploy_process.result == 'failed':
                    # failed
                    self.LOG.info('last process deploy finish, and failed')
                    self.pendings.remove(instance)
                    self.faileds.append(instance)
                    continue
                else:
                    if time.time() - time.mktime(time.strptime(deploy_process.start_time,'%Y-%m-%d %H:%M:%S')) >= self.single_deploy_timeout:
                        # time out
                        self.LOG.info('last process not deploy finish, but timeout')
                        deploy_process.result = 'timeout'
                        deploy_process.end_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                        deploy_process.save()
                        self.pendings.remove(instance)
                        self.faileds.append(instance)
                        continue
                    else:
                        # not time out, not deploy finish
                        self.LOG.info('last process not deploy finish, and not timeout')
                        is_finish = False
                        continue
        return is_finish
    
    def process(self):
        if not self.init():
            return False, 'Last version deploy failed, not allowed deploy to target version {0}.'.format(self.version)
  
        self.update_group()
        self.record_deploy()
        
        if self.is_exec_sql():
            if not self.exec_sql():
                self.LOG.error('group [{0}] service [{1}] upgrade to [{2}] exec sql failed.'.format(self.group, self.service, self.version))
                return False, 'Exec sql failed.'
        self.LOG.debug('group [{0}] service [{1}] upgrade to [{2}] exec sql success.'.format(self.group, self.service, self.version))
        
        if self.current_version == 'v0.0.0':
            self.modify_consul_deploy(self.version)
        else:
            self.modify_consul_deploy(self.current_version)

        self.get_single_deploy_min()
        self.LOG.debug('self.single_deploy_min is [{0}]'.format(self.single_deploy_min))
        
        if not self.deploy_instances:
            self.LOG.info('group [{0}] service [{1}] no instances to deploy'.format(self.group, self.service))
            return False, 'Has no instances to deploy.'

        while True:
            if self.is_last_process_finish(): # check last deploy process is finish or not
                self.LOG.info('last process finied')
                if self.is_continue(): # check is continue deploy or not
                    self.LOG.info('start next process')
                    self.allot_task()
                else:
                    break
            time.sleep(10)
        
        self.modify_consul_deploy(self.version)
        self.get_deploy_result()
        self.modify_deploy()
        self.LOG.info('deploy finiehd with result {0}'.format(self.deploy_result))
        if self.deploy_result == 'success':
            return True, 'Deploy success.'
        else:
            return False, 'Deploy failed.'
