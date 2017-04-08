#!/usr/bin/python
# -*-coding:utf-8-*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
# copyright 2015 Sengled, Inc.
# All Rights Reserved.

# @author: WShuai, Sengled, Inc.

from django.conf import settings
from django.views.decorators.csrf import requires_csrf_token
from sengladmin.tasks import consul_sync_datacenter,consul_add_group,consul_remove_datacenter,consul_sync_health,consul_sync_config,consul_sync_configs,consul_remove_config,pre_process_package,package_deploy,consul_sync_monitor,consul_remove_group,package_upload

import os
import time
import json
from sengladmin.models import Datacenter,Service,DeployGroup,Config,Package,Health,Monitor,Permission,DeployRecord,DeployProcess,Consignee,Event,Q
from commResponse import CommResponse
from commFile import ServicePackage
from commXml import XMLHandler
from commJenkins import JenkinsHandler
from userHandler import UserHandler

class OpsHandler(object):
    def __init__(self, request, LOG = None):
        self.request = request
        self.rsp_handler = CommResponse()
        self.user_handler = UserHandler(request)
        self.LOG = LOG
        return

    def all_resources(self, group_name = None):
        datacenters = Datacenter.objects.exclude('id').order_by('name')
        datacenters_instances = json.loads(datacenters.to_json())

        services = Service.objects.exclude('id').order_by('name')
        services_instances = json.loads(services.to_json())

        healths = Health.objects.exclude('id').order_by('name')
        healths_instances = json.loads(healths.to_json())

        monitors = Monitor.objects.exclude('id').order_by('name')
        monitors_instances = json.loads(monitors.to_json())

        group_instance = None
        groups_instance = None
        if group_name:
            groups = DeployGroup.objects(name = group_name).exclude('id').order_by('name')
            if groups:
                group = groups[0]
                group_instance = json.loads(group.to_json())
                group_instance['healthchecks'] = '\n'.join(group_instance['healthchecks'])
                group_instance['monitors'] = '\n'.join(group_instance['monitors'])
        else:
            groups = DeployGroup.objects.exclude('id').order_by('name')
            groups_instance = json.loads(groups.to_json())

        permissions = Permission.objects(superior = 'ROOT').exclude('id').order_by('name')
        permissions_instances = json.loads(permissions.to_json())

        rsp_body = {
            'rsp_body': {
                'datacenters': datacenters_instances,
                'services': services_instances,
                'healths': healths_instances,
                'monitors': monitors_instances,
                'group': group_instance,
                'groups': groups_instance,
                'permissions': permissions_instances,
            }
        }
        rsp = self.rsp_handler.generate_rsp_msg(200, rsp_body)
        return rsp

    def condition_resources(self, datacenter_name, service_name):
        if not datacenter_name or not service_name:
            rsp = self.rsp_handler.generate_rsp_msg(29001, None)
            return rsp

        groups = DeployGroup.objects(datacenter = datacenter_name, service = service_name).exclude('id').order_by('name')
        group_instances = json.loads(groups.to_json())
        
        package = Package.objects(service = service_name).exclude('id').order_by('version')
        package_instances = json.loads(package.to_json())
 
        rsp_body = {
            'rsp_body': {
                'groups': group_instances,
                'versions': package_instances,
            }
        }
        rsp = self.rsp_handler.generate_rsp_msg(200, rsp_body)
        return rsp

    def all_consignees(self):
        consignees = Consignee.objects.exclude('id').order_by('name')
        consignees_instances = json.loads(consignees.to_json())
        for consignee_instance in consignees_instances:
            if 'service' in consignee_instance.keys():
                consignee_instance['service'] = ','.join(consignee_instance['service'])
            if 'group' in consignee_instance.keys():
                consignee_instance['group'] = ','.join(consignee_instance['group'])
        rsp_body = {'rsp_body': {'consignees': consignees_instances}}
        rsp = self.rsp_handler.generate_rsp_msg(200, rsp_body)
        return rsp
    
    def get_consignee(self, name):
        consignees = Consignee.objects(name = name)
        if not consignees:
            rsp = self.rsp_handler.generate_rsp_msg(22002, None)
            return rsp
        consignee = consignees[0]

        services = Service.objects().exclude('id').order_by('name')
        services_instances = json.loads(services.to_json())

        consignee_instance = json.loads(consignee.to_json())
        rsp_body = {'rsp_body': {'consignee': consignee_instance, 'service': services_instances}}
        rsp = self.rsp_handler.generate_rsp_msg(200, rsp_body)
        return rsp

    def create_consignee(self, name, email, group, service):
        if not name:
            rsp = self.rsp_handler.generate_rsp_msg(29001, None)
            return rsp
        consignee = Consignee.objects(name = name)
        if consignee:
            rsp = self.rsp_handler.generate_rsp_msg(22001, None)
            return rsp
        consignee = Consignee(
            name = name,
            email = email,
            group = group,
            service = service
        )
        consignee.save()
        rsp = self.rsp_handler.generate_rsp_msg(200, None)
        return rsp

    def modify_consignee(self, name, email, group, service):
        consignees = Consignee.objects(name = name)
        if not consignees:
            rsp = self.rsp_handler.generate_rsp_msg(22002, None)
            return rsp
        consignee = consignees[0]
        consignee.email = email
        consignee.group = group
        consignee.service = service
        consignee.save()
        rsp = self.rsp_handler.generate_rsp_msg(200, None)
        return rsp

    def remove_consignee(self, name):
        consignees = Consignee.objects(name = name)
        if not consignees:
            rsp = self.rsp_handler.generate_rsp_msg(22002, None)
            return rsp
        consignee = consignees[0]
        consignee.delete()
        rsp = self.rsp_handler.generate_rsp_msg(200, None)
        return rsp

    def all_datacenters(self):
        datacenters = Datacenter.objects.exclude('id').order_by('name')
        datacenters_instances = json.loads(datacenters.to_json())
        rsp_body = {'rsp_body': {'datacenters': datacenters_instances}}
        rsp = self.rsp_handler.generate_rsp_msg(200, rsp_body)
        return rsp

    def get_datacenter(self, name):
        datacenters = Datacenter.objects(name = name)
        if not datacenters:
            rsp = self.rsp_handler.generate_rsp_msg(22002, None)
            return rsp
        datacenter = datacenters[0]
        datacenter_instance = json.loads(datacenter.to_json())
        rsp_body = {'rsp_body': {'datacenter': datacenter_instance}}
        rsp = self.rsp_handler.generate_rsp_msg(200, rsp_body)
        return rsp
        
    def remove_datacenter(self, authorize_code, name):
        if not self.user_handler.super_authorize(authorize_code):
            rsp = self.rsp_handler.generate_rsp_msg(29002, None)
            return rsp
        datacenters = Datacenter.objects(name = name)
        if not datacenters:
            rsp = self.rsp_handler.generate_rsp_msg(22002, None)
            return rsp
        datacenter = datacenters[0]
        groups = DeployGroup.objects(datacenter = datacenter.name)
        if groups:
            rsp = self.rsp_handler.generate_rsp_msg(22005, None)
            return rsp

        consul_remove_datacenter.delay(json.loads(datacenter.to_json()))

        datacenter.delete()
        rsp = self.rsp_handler.generate_rsp_msg(200, None)
        return rsp

    def create_datacenter(self,
            name,
            location,
            env,
            type,
            region,
            deploy_region,
            deploy_bucket,
            qurom_domain,
            qurom_port,
            qurom_cacert,
            qurom_cakey,
            agent_version,
            agent_file_path,
            agent_access_key,
            agent_secret_access
        ):
        if not name:
            rsp = self.rsp_handler.generate_rsp_msg(29001, None)
            return rsp
        datacenter = Datacenter.objects(name = name)
        if datacenter:
            rsp = self.rsp_handler.generate_rsp_msg(22001, None)
            return rsp

        agent_json = {
            'version': agent_version,
            'file_path': agent_file_path,
            'access_key_id': agent_access_key,
            'secret_access_key': agent_secret_access
        }
        deploy_json = {
            'region': deploy_region,
            'bucket': deploy_bucket
        }
        qurom_json = {
            'domain': qurom_domain,
            'port': qurom_port,
            'cacert': qurom_cacert,
            'cakey': qurom_cakey
        }
        datacenter = Datacenter(
            name = name,
            location = location,
            env = env,
            type = type,
            region = region,
            status = 'unlock',
            agent = agent_json,
            deploy = deploy_json,
            qurom = qurom_json
        )
        datacenter.save()
        rsp = self.rsp_handler.generate_rsp_msg(200, None)
        return rsp

    def modify_datacenter(self,
            name,
            location,
            env,
            type,
            region,
            deploy_region,
            deploy_bucket,
            qurom_domain,
            qurom_port,
            qurom_cacert,
            qurom_cakey,
            agent_version,
            agent_file_path,
            agent_access_key,
            agent_secret_access
        ):
        if not name:
            rsp = self.rsp_handler.generate_rsp_msg(29001, None)
            return rsp
        datacenters = Datacenter.objects(name = name)
        if not datacenters:
            rsp = self.rsp_handler.generate_rsp_msg(22002, None)
            return rsp
        datacenter = datacenters[0]

        datacenter.location = location
        datacenter.env = env
        datacenter.type = type
        datacenter.region = region
        datacenter.deploy['region'] = deploy_region
        datacenter.deploy['bucket'] = deploy_bucket
        datacenter.qurom['domain'] = qurom_domain
        datacenter.qurom['port'] = qurom_port
        datacenter.qurom['cacert'] = qurom_cacert
        datacenter.qurom['cakey'] = qurom_cakey
        datacenter.agent['version'] = agent_version
        datacenter.agent['file_path'] = agent_file_path
        datacenter.agent['access_key_id'] = agent_access_key
        datacenter.agent['secret_access_key'] = agent_secret_access
        datacenter.save()
        rsp = self.rsp_handler.generate_rsp_msg(200, None)
        return rsp

    def modify_datacenter_status(self, name, status):
        if not name or not status:
            rsp = self.rsp_handler.generate_rsp_msg(29001, None)
            return rsp
        datacenters = Datacenter.objects(name = name)
        if not datacenters:
            rsp = self.rsp_handler.generate_rsp_msg(22002, None)
            return rsp
        datacenter = datacenters[0]
        
        if datacenter.status == status:
            rsp = self.rsp_handler.generate_rsp_msg(22003, None)
            return rsp
        datacenter.status = status
        datacenter.save()
        rsp = self.rsp_handler.generate_rsp_msg(200, None)
        return rsp

    def sync_datacenter(self, name):
        if not name:
            rsp = self.rsp_handler.generate_rsp_msg(29001, None)
            return rsp
        datacenters = Datacenter.objects(name = name)
        if not datacenters:
            rsp = self.rsp_handler.generate_rsp_msg(22002, None)
            return rsp
        datacenter = datacenters[0]
        
        consul_sync_datacenter.delay(json.loads(datacenter.to_json()))
    
        rsp = self.rsp_handler.generate_rsp_msg(200, None)
        return rsp

    def all_services(self):
        services = Service.objects.exclude('id').order_by('name')
        services_instances = json.loads(services.to_json())
        for service in services_instances:
            service['datacenters'] = ','.join(service['datacenters'])
            #if 'build_env' in service.keys() and service['build_env']:
            #    service['build_env'] = '{0}: {1}'.format(service['build_env']['build_env_type'], service['build_env']['build_env_value'])
            #else:
            #    service['build_env'] = ''
        rsp_body = {'rsp_body': {'services': services_instances}}
        rsp = self.rsp_handler.generate_rsp_msg(200, rsp_body)
        return rsp

    def create_jenkins_job(
            self,
            service_name,
            service_desc,
            service_git_path,
            service_build_trigger,
            service_build_trigger_str,
            docker_image_id
        ):
        xml_handler = XMLHandler(settings.TEMPLATE_JENKINS_CONFIG_XML)
        xml_handler.load_xml()

        if service_desc:
            xml_handler.set_node_value('/project/description', service_desc)

        if service_git_path:
            xml_handler.set_node_value('/project/scm/userRemoteConfigs/hudson.plugins.git.UserRemoteConfig/url', service_git_path)

        self.LOG.debug('service_build_trigger is [{0}]'.format(service_build_trigger))
        if not service_build_trigger or service_build_trigger == 'manual':
            xml_handler.set_node_value('/project/triggers', None)
        else:
            xml_handler.set_node_value('/project/triggers/hudson.triggers.SCMTrigger/spec', service_build_trigger_str)

        cmd = 'sudo python {0} {1} {2} {3}'.format(settings.JENKINS_BUILD_TRIGGER, service_name, service_git_path, docker_image_id)
        xml_handler.set_node_value('/project/builders/hudson.tasks.Shell/command', cmd)

        save_xml_file = os.path.join('/tmp', '{0}_config.xml'.format(service_name))
        xml_handler.save_xml(save_xml_file)
        
        self.LOG.debug('host is {0}, port is {1}, user is {2}, pass is {3}'.format(settings.JENKINS_HOST, settings.JENKINS_PORT, settings.JENKINS_USER, settings.JENKINS_PASS))

        jenkins_handler = JenkinsHandler(settings.JENKINS_HOST, settings.JENKINS_PORT, settings.JENKINS_USER, settings.JENKINS_PASS)
        jenkins_handler.connect()
        self.LOG.debug('connect finished.')
        jenkins_handler.create_job(service_name, save_xml_file)
        os.remove(save_xml_file)
        self.LOG.debug('create finished.')
        return

    def delete_jenkins_job(self, service_name):
        jenkins_handler = JenkinsHandler(settings.JENKINS_HOST, settings.JENKINS_PORT, settings.JENKINS_USER, settings.JENKINS_PASS)
        jenkins_handler.connect()
        jenkins_handler.delete_job(service_name)
        return

    def create_service(self,
            name,
            description,
            git_path,
            #build_env_type,
            #build_env_value,
            build_trigger,
            build_trigger_str,
            docker_image_id):
        if not name:
            rsp = self.rsp_handler.generate_rsp_msg(29001, None)
            return rsp
        service = Service.objects(name = name)
        if service:
            rsp = self.rsp_handler.generate_rsp_msg(22001, None)
            return rsp
        
        #if build_env_type == 'NULL' or build_env_value == 'NULL':
        #    build_env = {}
        #else:
        #    build_env = {
        #        'build_env_type': build_env_type,
        #        'build_env_value': build_env_value
        #    }

        service = Service(
            name = name,
            description = description,
            git_path = git_path,
            #build_env = build_env,
            build_trigger = build_trigger if build_trigger == 'manual' else build_trigger_str,
            build_docker_image = docker_image_id,
            status = 'unlock'
        )
        service.save()

        self.create_jenkins_job(name, description, git_path, build_trigger, build_trigger_str, docker_image_id)
        rsp = self.rsp_handler.generate_rsp_msg(200, None)
        return rsp

    def get_service(self, name):
        services = Service.objects(name = name)
        if not services:
            rsp = self.rsp_handler.generate_rsp_msg(22002, None)
            return rsp
        service = services[0]
        service_instance = json.loads(service.to_json())
        rsp_body = {'rsp_body': {'service': service_instance}}
        rsp = self.rsp_handler.generate_rsp_msg(200, rsp_body)
        return rsp

    def modify_service_status(self, name, status):
        if not name or not status:
            rsp = self.rsp_handler.generate_rsp_msg(29001, None)
            return rsp
        services = Service.objects(name = name)
        if not services:
            rsp = self.rsp_handler.generate_rsp_msg(22002, None)
            return rsp
        service = services[0]

        if service.status == status:
            rsp = self.rsp_handler.generate_rsp_msg(22003, None)
            return rsp
        service.status = status
        service.save()
        rsp = self.rsp_handler.generate_rsp_msg(200, None)
        return rsp

    def modify_service(self,
            name,
            description,
            git_path,
            #build_env_type,
            #build_env_value,
            build_trigger,
            build_trigger_str,
            docker_image_id
        ):
        if not name:
            rsp = self.rsp_handler.generate_rsp_msg(29001, None)
            return rsp
        services = Service.objects(name = name)
        if not services:
            rsp = self.rsp_handler.generate_rsp_msg(22002, None)
            return rsp

        service = services[0]
        service.description = description
        service.git_path = git_path
        #if build_env_type == 'NULL' or build_env_value == 'NULL':
        #    service.build_env = {}
        #else:
        #    service.build_env = {
        #        'build_env_type': build_env_type,
        #        'build_env_value': build_env_value
        #    }
        service.build_trigger = build_trigger if build_trigger == 'manual' else build_trigger_str
        service.build_docker_image = docker_image_id
        service.save()

        self.create_jenkins_job(name, description, git_path, build_trigger, build_trigger_str, docker_image_id)
        rsp = self.rsp_handler.generate_rsp_msg(200, None)
        return rsp

    def remove_service(self, name):
        services = Service.objects(name = name)
        if not services:
            rsp = self.rsp_handler.generate_rsp_msg(22002, None)
            return rsp
        service = services[0]
        service.delete()
        self.delete_jenkins_job(name)
        rsp = self.rsp_handler.generate_rsp_msg(200, None)
        return rsp

    def all_groups(self, datacenter):
        if not datacenter:
            groups = DeployGroup.objects.exclude('id').order_by('name')
        else:
            groups = DeployGroup.objects(datacenter = datacenter).exclude('id').order_by('name')
        groups_instances = json.loads(groups.to_json())
        rsp_body = {'rsp_body': {'groups': groups_instances}}
        rsp = self.rsp_handler.generate_rsp_msg(200, rsp_body)
        return rsp
        
    def create_group(self,
            name,
            service,
            version,
            datacenter,
            rm_type,
            rm_name,
            deploy_type,
            deploy_value
        ):
        if not deploy_value:
            rsp = self.rsp_handler.generate_rsp_msg(29001, None)
        else:
            if deploy_value[0] != '-':
                if not name or not deploy_value.isdigit():
                    rsp = self.rsp_handler.generate_rsp_msg(29001, None)
                    return rsp
            else:
                if not name or not deploy_value[1:].isdigit():
                    rsp = self.rsp_handler.generate_rsp_msg(29001, None)
                    return rsp
        group = DeployGroup.objects(name = name)
        if group:
            rsp = self.rsp_handler.generate_rsp_msg(22001, None)
            return rsp

        package = Package.objects(service = service, version = version)
        if not package:
            rsp = self.rsp_handler.generate_rsp_msg(22004, None)
            return rsp

        group = DeployGroup(
            name = name,
            datacenter = datacenter,
            service = service,
            version = version,
            group = {'type': rm_type, 'name': rm_name},
            deploy = {'type': deploy_type, 'value': int(deploy_value)}
        )
        group.save()
    
        consul_add_group.delay(json.loads(group.to_json()))

        rsp = self.rsp_handler.generate_rsp_msg(200, None)
        return rsp

    def get_group(self, name):
        groups = DeployGroup.objects(name = name)
        if not groups:
            rsp = self.rsp_handler.generate_rsp_msg(22002, None)
            return rsp
        group = groups[0]
        group_instance = json.loads(group.to_json())
        group_instance['healthchecks'] = '\n'.join(group_instance['healthchecks'])
        group_instance['monitors'] = '\n'.join(group_instance['monitors'])
        rsp_body = {'rsp_body': {'group': group_instance}}
        rsp = self.rsp_handler.generate_rsp_msg(200, rsp_body)
        return rsp
        
    def modify_group(self, name, rm_type, rm_name, deploy_type, deploy_value):
        if not deploy_value:
            rsp = self.rsp_handler.generate_rsp_msg(29001, None)
        else:
            if deploy_value[0] != '-':
                if not name or not deploy_value.isdigit():
                    rsp = self.rsp_handler.generate_rsp_msg(29001, None)
                    return rsp
            else:
                if not name or not deploy_value[1:].isdigit():
                    rsp = self.rsp_handler.generate_rsp_msg(29001, None)
                    return rsp
        groups = DeployGroup.objects(name = name) 
        if not groups:
            rsp = self.rsp_handler.generate_rsp_msg(22002, None)
            return rsp
        group = groups[0]  

        group.group['type'] = rm_type
        group.group['name'] = rm_name
        group.deploy['type'] = deploy_type
        group.deploy['value'] = int(deploy_value)
        group.save()
        rsp = self.rsp_handler.generate_rsp_msg(200, None)
        return rsp

    def remove_group(self, authorize_code, name):
        if not self.user_handler.super_authorize(authorize_code):
            rsp = self.rsp_handler.generate_rsp_msg(29002, None)
            return rsp
        groups = DeployGroup.objects(name = name)
        if not groups:
            rsp = self.rsp_handler.generate_rsp_msg(22002, None)
            return rsp
        group = groups[0]
        
        datacenters = Datacenter.objects(name = group.datacenter)
        if not datacenters:
            rsp = self.rsp_handler.generate_rsp_msg(29001, None)
            return rsp
        datacenter_object = datacenters[0]

        healths = Health.objects(name__in = group.healthchecks)
        for health in healths:
            try:
                health.groups.remove(group.name)
            except:
                pass
            if not health.groups:
                health.associate = False
            health.save()

        monitors = Monitor.objects(name__in = group.monitors)
        for monitor in monitors:
            monitor.groups.remove(group.name)
            if not monitor.groups:
                monitor.associate = False
            monitor.save()

        consul_remove_group.delay(datacenter = json.loads(datacenter_object.to_json()), group_name = group.name)

        group.delete()
        rsp = self.rsp_handler.generate_rsp_msg(200, None)
        return rsp

    def all_configs(self, config_datacenter, config_domain):
        if not config_datacenter or not config_domain:
            print 0, config_datacenter, config_domain
            configs = Config.objects.exclude('id').order_by('name')
        else:
            print 1,config_datacenter, config_domain
            configs = Config.objects(Q(datacenter = config_datacenter) & (Q(domain = config_domain) | Q(domain = 'GLOBAL'))).exclude('id').order_by('name')
        configs_instances = json.loads(configs.to_json())
        rsp_body = {'rsp_body': {'configs': configs_instances}}
        rsp = self.rsp_handler.generate_rsp_msg(200, rsp_body)
        return rsp
        

    def create_config(self, key, description, value, consul_key, consul_value, datacenter, domain):
        if not key:
            rsp = self.rsp_handler.generate_rsp_msg(29001, None)
            return rsp
        config = Config.objects(key = key, datacenter = datacenter, domain = domain)
        if config:
            rsp = self.rsp_handler.generate_rsp_msg(23001, None)
            return rsp

        datacenter_objects = Datacenter.objects(name = datacenter)
        if not datacenter_objects:
            rsp = self.rsp_handler.generate_rsp_msg(29001, None)
            return rsp
        datacenter_object  = datacenter_objects[0]

        config = Config(
            key = key,
            description = description if description else 'DEFAULT',
            value = value,
            consul_key = consul_key,
            consul_value = consul_value,
            datacenter = datacenter,
            domain = domain
        )
        config.save()

        if consul_key:
            if domain == 'GLOBAL':
                groups = DeployGroup.objects(datacenter = datacenter)
            else:
                groups = DeployGroup.objects(service = domain)
            for group in groups:
                consul_sync_config.delay(datacenter = json.loads(datacenter_object.to_json()), group_name = group.name, config_value = value, config_consul_key = consul_key)
       
        rsp = self.rsp_handler.generate_rsp_msg(200, None)
        return rsp

    def get_config(self, key, datacenter, domain):
        if not key:
            rsp = self.rsp_handler.generate_rsp_msg(29001, None)
            return rsp
        configs = Config.objects(key = key, datacenter = datacenter, domain = domain)
        if not configs:
            rsp = self.rsp_handler.generate_rsp_msg(23002, None)
            return rsp
        config = configs[0]
        config_instance = json.loads(config.to_json())
        rsp_body = {'rsp_body': {'config': config_instance}}
        rsp = self.rsp_handler.generate_rsp_msg(200, rsp_body)
        return rsp

    def modify_config(self, key, description, value, consul_value, datacenter, domain):
        if not key:
            rsp = self.rsp_handler.generate_rsp_msg(29001, None)
            return rsp
        configs = Config.objects(key = key, datacenter = datacenter, domain = domain)
        if not configs:
            rsp = self.rsp_handler.generate_rsp_msg(23002, None)
            return rsp
        config = configs[0]  

        datacenter_objects = Datacenter.objects(name = datacenter)
        if not datacenter_objects:
            rsp = self.rsp_handler.generate_rsp_msg(29001, None)
            return rsp
        datacenter_object  = datacenter_objects[0]

        config['description'] = description if description else 'DEFAULT'
        config['value'] = value
        config['consul_value'] = consul_value
        config.save()

        if domain == 'GLOBAL':
            groups = DeployGroup.objects(datacenter = datacenter)
        else:
            groups = DeployGroup.objects(service = domain)
        for group in groups:
            consul_sync_config.delay(datacenter = json.loads(datacenter_object.to_json()), group_name = group.name, config_value = value, config_consul_key = config.consul_key)

        rsp = self.rsp_handler.generate_rsp_msg(200, None)
        return rsp

    def remove_config(self, key, datacenter, domain):
        if not key:
            rsp = self.rsp_handler.generate_rsp_msg(29001, None)
            return rsp
        configs = Config.objects(key = key, datacenter = datacenter, domain = domain)
        if not configs:
            rsp = self.rsp_handler.generate_rsp_msg(23002, None)
            return rsp
        config = configs[0]

        datacenter_objects = Datacenter.objects(name = datacenter)
        if not datacenter_objects:
            rsp = self.rsp_handler.generate_rsp_msg(29001, None)
            return rsp
        datacenter_object  = datacenter_objects[0]

        config.delete()

        if domain == 'GLOBAL':
            groups = DeployGroup.objects(datacenter = datacenter)
        else:
            groups = DeployGroup.objects(service = domain)
        for group in groups:
            consul_remove_config.delay(datacenter = json.loads(datacenter_object.to_json()), group_name = group.name, config_name = key)

        rsp = self.rsp_handler.generate_rsp_msg(200, None)
        return rsp

    def all_healths(self):
        healths = Health.objects.exclude('id').order_by('name')
        healths_instances = json.loads(healths.to_json())
        rsp_body = {'rsp_body': {'healths': healths_instances}}
        rsp = self.rsp_handler.generate_rsp_msg(200, rsp_body)
        return rsp

    def create_health(self,
            name,
            type,
            value,
            interval,
            timeout,
            pending,
            healthy_threshold,
            unhealthy_threshold,
            failback
        ):
        if not name:
            rsp = self.rsp_handler.generate_rsp_msg(29001, None)
            return rsp
        health = Health.objects(name = name)
        if health:
            rsp = self.rsp_handler.generate_rsp_msg(23001, None)
            return rsp
        health = Health(
            name = name,
            type = type,
            value = value,
            interval = int(interval),
            timeout = int(timeout),
            pending = int(pending),
            healthy_threshold = int(healthy_threshold),
            unhealthy_threshold = int(unhealthy_threshold),
            failback = failback,
            associate = False
        )
        health.save()
        rsp = self.rsp_handler.generate_rsp_msg(200, None)
        return rsp

    def get_health(self, name):
        healths = Health.objects(name = name)
        if not healths:
            rsp = self.rsp_handler.generate_rsp_msg(22002, None)
            return rsp
        health = healths[0]
        health_instance = json.loads(health.to_json())
        rsp_body = {'rsp_body': {'health': health_instance}}
        rsp = self.rsp_handler.generate_rsp_msg(200, rsp_body)
        return rsp

    def modify_health(self,
            name,
            type,
            value,
            interval,
            timeout,
            pending,
            healthy_threshold,
            unhealthy_threshold,
            failback
        ):
        if not name:
            rsp = self.rsp_handler.generate_rsp_msg(29001, None)
            return rsp
        healths = Health.objects(name = name)
        if not healths:
            rsp = self.rsp_handler.generate_rsp_msg(22002, None)
            return rsp
        health = healths[0]
        health.type = type
        health.value = value
        health.interval = int(interval)
        health.timeout = int(timeout)
        health.pending = int(pending)
        health.healthy_threshold = int(healthy_threshold)
        health.unhealthy_threshold = int(unhealthy_threshold)
        health.failback = failback
        self.sync_health_to_consul(json.loads(health.to_json()), health.groups)
        health.save()
        rsp = self.rsp_handler.generate_rsp_msg(200, None)
        return rsp

    def sync_health_to_consul(self, health, group_names):
        if not group_names:
            return

        for group_name in group_names:
            groups = DeployGroup.objects(name = group_name)
            if not groups:
                continue
            group = groups[0]
            if not group.healthchecks:
                continue
            
            datacenters = Datacenter.objects(name = group.datacenter)
            if not datacenters:
                continue
            datacenter = datacenters[0]

            healths = Health.objects(name__in = group.healthchecks)
            health_instances = json.loads(healths.to_json())
            for index, single_instance in enumerate(health_instances):
                if single_instance['name'] == health['name']:
                    break
            del health_instances[index]
            temp_health = health.copy()
            health_instances.append(temp_health)

            for single_instance in health_instances:
                #single_instance[single_instance['type']] = single_instance['value']
                single_instance['associate_service'] = single_instance['associate'] if single_instance['associate'] else False
                single_instance['pending'] = single_instance['pending']
                single_instance['interval'] = single_instance['interval']
                single_instance['timeout'] = single_instance['timeout']
                single_instance['healthy_threshold'] = single_instance['healthy_threshold']
                single_instance['unhealthy_threshold'] = single_instance['unhealthy_threshold']
                del single_instance['associate']
                try:
                    single_instance.pop('_id')
                    single_instance.pop('groups')
                except:
                    continue
            self.LOG.info('health_instances is {0}'.format(health_instances))
            consul_sync_health.delay(datacenter = json.loads(datacenter.to_json()), group_name = group_name, healths = health_instances)
        return

    def remove_health(self, name):
        healths = Health.objects(name = name)
        if not healths:
            rsp = self.rsp_handler.generate_rsp_msg(22002, None)
            return rsp
        health = healths[0]
        if health.associate:
            rsp = self.rsp_handler.generate_rsp_msg(22006, None)
            return rsp
        health.delete()
        rsp = self.rsp_handler.generate_rsp_msg(200, None)
        return rsp

    def link_health(self):
        rsp = self.rsp_handler.generate_rsp_msg(200, None)
        return rsp

    def unlink_health(self):
        rsp = self.rsp_handler.generate_rsp_msg(200, None)
        return rsp

    def all_monitors(self):
        monitors = Monitor.objects.exclude('id').order_by('name')
        monitors_instances = json.loads(monitors.to_json())
        rsp_body = {'rsp_body': {'monitors': monitors_instances}}
        rsp = self.rsp_handler.generate_rsp_msg(200, rsp_body)
        return rsp

    def create_monitor(self, name, type, value):
        if not name:
            rsp = self.rsp_handler.generate_rsp_msg(29001, None)
            return rsp
        monitor = Monitor.objects(name = name)
        if monitor:
            rsp = self.rsp_handler.generate_rsp_msg(23001, None)
            return rsp
        monitor = Monitor(
            name = name,
            type = type,
            value = value,
            associate = False
        )
        monitor.save()
        rsp = self.rsp_handler.generate_rsp_msg(200, None)
        return rsp

    def get_monitor(self, name):
        monitors = Monitor.objects(name = name)
        if not monitors:
            rsp = self.rsp_handler.generate_rsp_msg(22002, None)
            return rsp
        monitor = monitors[0]
        monitor_instance = json.loads(monitor.to_json())
        rsp_body = {'rsp_body': {'monitor': monitor_instance}}
        rsp = self.rsp_handler.generate_rsp_msg(200, rsp_body)
        return rsp

    def modify_monitor(self, name, type, value):
        if not name:
            rsp = self.rsp_handler.generate_rsp_msg(29001, None)
            return rsp
        monitors = Monitor.objects(name = name)
        if not monitors:
            rsp = self.rsp_handler.generate_rsp_msg(22002, None)
            return rsp
        monitor = monitors[0]
        monitor.type = type
        monitor.value = value
        self.sync_monitor_to_consul(json.loads(monitor.to_json()), monitor.groups)
        monitor.save()
        rsp = self.rsp_handler.generate_rsp_msg(200, None)
        return rsp

    def sync_monitor_to_consul(self, monitor, group_names):
        if not group_names:
            return 
                    
        for group_name in group_names:
            groups = DeployGroup.objects(name = group_name)                                                     
            if not groups:
                continue
            group = groups[0]                                                                                   
            if not group.monitors:
                continue
                
            datacenters = Datacenter.objects(name = group.datacenter)
            if not datacenters:
                continue
            datacenter = datacenters[0]
                        
            monitors = Monitor.objects(name__in = group.monitors)
            monitor_instances = json.loads(monitors.to_json())
            for index, single_instance in enumerate(monitor_instances):
                if single_instance['name'] == monitor['name']:
                    break
            del monitor_instances[index]
            monitor_instances.append(monitor)

            for single_instance in monitor_instances:
                try:
                    single_instance.pop('_id')
                    single_instance.pop('groups')
                except:
                    continue
            consul_sync_monitor.delay(datacenter = json.loads(datacenter.to_json()), group_name = group_name, monitors = monitor_instances)
        return

    def remove_monitor(self, name):
        monitors = Monitor.objects(name = name)
        if not monitors:
            rsp = self.rsp_handler.generate_rsp_msg(22002, None)
            return rsp
        monitor = monitors[0]
        if monitor.associate:
            rsp = self.rsp_handler.generate_rsp_msg(22007, None)
            return rsp
        monitor.delete()
        rsp = self.rsp_handler.generate_rsp_msg(200, None)
        return rsp

    def sync_health(self, group_name, health_names):
        self.LOG.debug('group_name is {0}'.format(group_name))
       
        if not group_name or not health_names:
            rsp = self.rsp_handler.generate_rsp_msg(29001, None)
            return rsp
        groups = DeployGroup.objects(name = group_name)
        if not groups:
            rsp = self.rsp_handler.generate_rsp_msg(22002, None)
            return rsp
        group = groups[0]

        del_healths = list(set(group.healthchecks) - (set(health_names) & set(group.healthchecks)))

        datacenters = Datacenter.objects(name = group.datacenter)
        if not datacenters:
            rsp = self.rsp_handler.generate_rsp_msg(22002, None)
            return rsp
        datacenter = datacenters[0]

        group.healthchecks = health_names
        group.save()

        healths = Health.objects(name__in = del_healths)
        for health in healths:
            if health.groups and group_name in health.groups:
                health.groups.remove(group_name)
            if not health.groups:
                health.associate = False
            health.save()

        if health_names:
            healths = Health.objects(name__in = health_names)
            for health in healths:
                health.associate = True
                if health.groups:
                    health.groups.append(group_name)
                    health.groups = list(set(health.groups))
                else:
                    health.groups = [group_name]
                health.save()            

            health_instances = None
            if healths:
                health_instances = json.loads(healths.to_json())
                for single_instance in health_instances:
                    #single_instance[single_instance['type']] = single_instance['value']
                    single_instance['associate_service'] = single_instance['associate']
                    single_instance['pending'] = single_instance['pending']
                    single_instance['interval'] = single_instance['interval']
                    single_instance['timeout'] = single_instance['timeout']
                    single_instance['healthy_threshold'] = single_instance['healthy_threshold']
                    single_instance['unhealthy_threshold'] = single_instance['unhealthy_threshold']
                    del single_instance['associate']
                    try:
                        single_instance.pop('_id')
                        single_instance.pop('groups')
                    except:
                        continue
            consul_sync_health.delay(datacenter = json.loads(datacenter.to_json()), group_name = group.name, healths = health_instances)

        rsp = self.rsp_handler.generate_rsp_msg(200, None)
        return rsp

    def sync_monitor(self, group_name, monitor_names):
        self.LOG.debug('group_name is {0}'.format(group_name))

        if not group_name or not monitor_names:
            rsp = self.rsp_handler.generate_rsp_msg(29001, None)
            return rsp
        groups = DeployGroup.objects(name = group_name)
        if not groups:
            rsp = self.rsp_handler.generate_rsp_msg(22002, None)
            return rsp
        group = groups[0]

        del_monitors = list(set(group.monitors) - (set(monitor_names) & set(group.monitors)))

        datacenters = Datacenter.objects(name = group.datacenter)
        if not datacenters:
            rsp = self.rsp_handler.generate_rsp_msg(22002, None)
            return rsp
        datacenter = datacenters[0]

        group.monitors = monitor_names
        group.save()

        monitors = Monitor.objects(name__in = del_monitors)
        for monitor in monitors:
            if monitor.groups and group_name in monitor.groups:
                monitor.groups.remove(group_name)
            if not monitor.groups:
                monitor.associate = False
            monitor.save()

        if monitor_names:
            monitors = Monitor.objects(name__in = monitor_names)
            for monitor in monitors:
                monitor.associate = True
                if monitor.groups:
                    monitor.groups.append(group_name)
                    monitor.groups = list(set(monitor.groups))
                else:
                    monitor.groups = [group_name]
                monitor.save()

            monitor_instances = None
            if monitors:
                monitor_instances = json.loads(monitors.to_json())
                for single_instance in monitor_instances:
                    try:
                        single_instance.pop('_id')
                        single_instance.pop('groups')
                    except:
                        continue
            consul_sync_monitor.delay(datacenter = json.loads(datacenter.to_json()), group_name = group.name, monitors = monitor_instances)

        rsp = self.rsp_handler.generate_rsp_msg(200, None)
        return rsp

    def sync_config(self, group_name):
        groups = DeployGroup.objects(name = group_name)
        if not groups:
            rsp = self.rsp_handler.generate_rsp_msg(22002, None)
            return rsp
        group = groups[0]

        datacenters = Datacenter.objects(name = group.datacenter)
        if not datacenters:
            rsp = self.rsp_handler.generate_rsp_msg(22002, None)
            return rsp
        datacenter = datacenters[0]

        configs = Config.objects(datacenter = group.datacenter, domain = group.service)
        configs = Config.objects(Q(datacenter = group.datacenter) & (Q(domain = group.service) | Q(domain = 'GLOBAL')))

        consul_add_group.delay(json.loads(group.to_json()))
        consul_sync_configs.delay(datacenter = json.loads(datacenter.to_json()), group_name = group.name, configs = json.loads(configs.to_json()))
        rsp = self.rsp_handler.generate_rsp_msg(200, None)
        return rsp
        
    def all_packages(self):
        packages = Package.objects.exclude('id').order_by('name')
        packages_instances = json.loads(packages.to_json())
        rsp_body = {'rsp_body': {'packages': packages_instances}}
        rsp = self.rsp_handler.generate_rsp_msg(200, rsp_body)
        return rsp

    def create_package(self, service, version, md5, region, bucket, file_path):
        if not service or not version:
            rsp = self.rsp_handler.generate_rsp_msg(29001, None)
            return rsp
        package = Package.objects(service = service, version = version)
        if package:
            rsp = self.rsp_handler.generate_rsp_msg(24001, None)
            return rsp
        package = Package(
            service = service,
            version = version,
            md5 = {'source': md5},
            region = region,
            bucket = bucket,
            file_path = file_path,
            time = time.strftime('%Y-%m-%d %H:%M:%S')
        )
        package.save()
        
        pre_process_package.delay(package = json.loads(package.to_json()))
        
        rsp = self.rsp_handler.generate_rsp_msg(200, None)
        return rsp

    def remove_package(self, authorize_code, service, version):
        if not self.user_handler.super_authorize(authorize_code):
            rsp = self.rsp_handler.generate_rsp_msg(29002, None)
            return rsp
        packages = Package.objects(service = service, version = version)
        if not packages:
            rsp = self.rsp_handler.generate_rsp_msg(24002, None)
            return rsp
        package = packages[0]
        try:
            deploy_status = [deploy['status'] for deploy in package.status['deploy']]        
            if 'deploying' in deploy_status:
                rsp = self.rsp_handler.generate_rsp_msg(24003, None)
                return rsp
        except:
            pass
        package.delete()
        rsp = self.rsp_handler.generate_rsp_msg(200, None)
        return rsp

    def get_package(self, service, version):
        packages = Package.objects(service = service, version = version)
        if not packages:
            rsp = self.rsp_handler.generate_rsp_msg(24002, None)
            return rsp
        package = packages[0]
        package_instance = json.loads(package.to_json())
        rsp_body = {'rsp_body': {'package': package_instance}}
        rsp = self.rsp_handler.generate_rsp_msg(200, rsp_body)
        return rsp

    def get_audit(self, service, version):
        packages = Package.objects(service = service, version = version)
        if not packages:
            rsp = self.rsp_handler.generate_rsp_msg(24002, None)
            return rsp
        package = packages[0]
        package_instance = json.loads(package.to_json())
        if package_instance['audit']:
            if 'port' in package_instance['audit'].keys():
                package_instance['audit']['port'] = '\n'.join(package_instance['audit']['port'])
            if 'config' in package_instance['audit'].keys():
                package_instance['audit']['config'] = '\n'.join(package_instance['audit']['config'])
        rsp_body = {'rsp_body': {'package': package_instance}}
        rsp = self.rsp_handler.generate_rsp_msg(200, rsp_body)
        return rsp

    def get_audit_sub(self, status):
        pass_packages = []
        refuse_packages = []
        wait_packages = []
        packages = Package.objects()
        for package in packages:
            if package.status:
                if package.status['sql'] == 'pass' and package.status['port'] == 'pass' and package.status['config'] == 'pass' and package.status['md5'] == 'pass':
                    pass_packages.append(json.loads(package.to_json()))
                elif package.status['sql'] == 'refuse' or package.status['port'] == 'refuse' or package.status['config'] == 'refuse' or package.status['md5'] == 'refuse':
                    refuse_packages.append(json.loads(package.to_json()))
                else:
                    wait_packages.append(json.loads(package.to_json()))
        if status == 'pass':
            packages_instances = pass_packages
        elif status == 'refuse':
            packages_instances = refuse_packages
        elif status == 'wait':
            packages_instances = wait_packages
        else:
            packages_instances = []
        rsp_body = {'rsp_body': {'packages': packages_instances}}
        rsp = self.rsp_handler.generate_rsp_msg(200, rsp_body)
        return rsp   

    def audit(self, account, authorize_code, service, version, type, status):
        if not self.user_handler.ordinary_authorize(account, authorize_code):
            rsp = self.rsp_handler.generate_rsp_msg(29002, None)
            return rsp

        packages = Package.objects(service = service, version = version)
        if not packages:
            rsp = self.rsp_handler.generate_rsp_msg(24002, None)
            return rsp
        package = packages[0]
        if package.status['sql'] == 'refuse' or package.status['port'] == 'refuse' or package.status['config'] == 'refuse':
            rsp = self.rsp_handler.generate_rsp_msg(24004, None)
            return rsp

        datacenters = Datacenter.objects(env = 'dev', region = package['region'])
        if not datacenters:
            rsp = self.rsp_handler.generate_rsp_msg(22002, None)
            return rsp
        datacenter = datacenters[0]

        # audit
        if status == 'pass':
            file_name = os.path.basename(package.file_path).replace('tar.gz', '%s.tar.gz' % version)
            local_file_path = os.path.join(settings.PACKAGE_SAVE_PATH, service, file_name)
            #service_package = ServicePackage(service, version, package.region, package.bucket, package.file_path, local_file_path, package.md5['source'], self.LOG)
            service_package = ServicePackage(json.loads(package.to_json()), local_file_path, json.loads(datacenter.to_json()), LOG = self.LOG)
            service_package.uncompress()
            if type == 'port':
                service_package.pass_port()
                update_status = 'pass'
                self.LOG.debug('{0} status is {1}'.format(type, service_package.endpoint_status))
            elif type == 'config':
                service_package.audit_config()
                update_status = service_package.config_status
                self.LOG.debug('{0} status is {1}'.format(type, service_package.config_status))
            service_package.clear()
        else:
            update_status = status
            #package.audit = {}

        package.status[type] = update_status
        package.save()
        if package.status['sql'] == 'pass' and package.status['port'] == 'pass' and package.status['config'] == 'pass':
            package_deploy.delay(package = json.loads(package.to_json()), target_env = 'dev', operator = 'auto')
        rsp = self.rsp_handler.generate_rsp_msg(200, None)
        return rsp

    def audit_force(self, authorize_code, service, version):
        if not self.user_handler.super_authorize(authorize_code):
            rsp = self.rsp_handler.generate_rsp_msg(29002, None)
            return rsp
        
        packages = Package.objects(service = service, version = version)
        if not packages:
            rsp = self.rsp_handler.generate_rsp_msg(24002, None)
            return rsp
        package = packages[0]
        
        package.status['sql'] = 'pass'
        package.status['port'] = 'pass'
        package.status['config'] = 'pass'
        package.save()
        package_deploy.delay(package = json.loads(package.to_json()), target_env = 'dev', operator = 'auto')
        rsp = self.rsp_handler.generate_rsp_msg(200, None)
        return rsp

    def deploy(self, datacenter_name, service_name, group_name, version, operator):
        if not datacenter_name or not service_name or not version:
            rsp = self.rsp_handler.generate_rsp_msg(29001, None)
            return rsp

        datacenters = Datacenter.objects(name = datacenter_name)
        if not datacenters:
            rsp = self.rsp_handler.generate_rsp_msg(22008, None)
            return rsp
        datacenter = datacenters[0]

        services = Service.objects(name = service_name)
        if not services:
            rsp = self.rsp_handler.generate_rsp_msg(22010, None)
            return rsp
        service = services[0]

        packages = Package.objects(service = service_name, version = version)
        if not packages:
            rsp = self.rsp_handler.generate_rsp_msg(24002, None)
            return rsp
        package = packages[0]

        ret = self.verify_deploy(datacenter.env, package)
        if ret == 200:
            #package_deploy.delay(package = json.loads(package.to_json()), target_env = datacenter.env, operator = operator)
            package_deploy.delay(package = json.loads(package.to_json()), target_env = datacenter.env, operator = operator, datacenter_name = datacenter.name)

        rsp = self.rsp_handler.generate_rsp_msg(ret, None)
        return rsp

    def verify_deploy(self, env, package_object):
        ret = 200
        if env == 'test':
            status_set = set(package_object.status.values())
            if len(status_set) == 1 and 'pass' in status_set:
                ret = 200
            else:
                ret = 25001
        elif env == 'production':
            if package_object.testing == 'pass':
                ret = 200
            else:
                ret = 25002
        return ret

    def deploy_upload(self, datacenter_name, service_name, version, operator):
        if not datacenter_name or not service_name or not version:
            rsp = self.rsp_handler.generate_rsp_msg(29001, None)
            return rsp
     
        datacenters = Datacenter.objects(name = datacenter_name)
        if not datacenters:
            rsp = self.rsp_handler.generate_rsp_msg(22008, None)
            return rsp
        datacenter = datacenters[0]

        services = Service.objects(name = service_name)
        if not services:
            rsp = self.rsp_handler.generate_rsp_msg(22010, None)
            return rsp
        service = services[0]

        packages = Package.objects(service = service_name, version = version)
        if not packages:
            rsp = self.rsp_handler.generate_rsp_msg(24002, None)
            return rsp
        package = packages[0]

        ret = self.verify_deploy(datacenter.env, package)
        if ret == 200:
            package_upload.delay(
                datacenter = json.loads(datacenter.to_json()),
                package = json.loads(package.to_json()),
                operator = operator
            )

        rsp = self.rsp_handler.generate_rsp_msg(ret, None)
        return rsp

    def all_deploy_record(self):
        deploy_records = DeployRecord.objects.order_by('strat_time')
        deploy_records_instances = json.loads(deploy_records.to_json())
        rsp_body = {'rsp_body': {'deploy_records': deploy_records_instances}}
        rsp = self.rsp_handler.generate_rsp_msg(200, rsp_body)
        return rsp

    def get_deploy_record(self, deploy_id):
        deploy_records = DeployRecord.objects(deploy_id = deploy_id)
        if not deploy_records:
            rsp = self.rsp_handler.generate_rsp_msg(22002, None)
            return rsp
        deploy_record = deploy_records[0]
        deploy_record_instance = json.loads(deploy_record.to_json())
        rsp_body = {'rsp_body': {'deploy_record': deploy_record_instance}}
        rsp = self.rsp_handler.generate_rsp_msg(200, rsp_body)
        return rsp

    def all_deploy_process(self):
        deploy_processes= DeployProcess.objects.order_by('deploy_id')
        deploy_processes_instances = json.loads(deploy_processes.to_json())
        rsp_body = {'rsp_body': {'deploy_processes': deploy_processes_instances}}
        rsp = self.rsp_handler.generate_rsp_msg(200, rsp_body)
        return rsp

    def modify_deploy_process(self, deploy_id, deploy_ip, deploy_status):
        deploy_processes = DeployProcess.objects(deploy_id = deploy_id, instance = deploy_ip)
        if not deploy_processes:
            rsp = self.rsp_handler.generate_rsp_msg(22002, None)
            return rsp
        deploy_process = deploy_processes[0]
        
        deploy_process.result = deploy_status
        deploy_process.end_time = time.strftime('%Y-%m-%d %H:%M:%S')
        deploy_process.save()
        
        rsp = self.rsp_handler.generate_rsp_msg(200, None)
        return rsp

    def create_event(self, event_id, description, additional, additional2, additional3, group_name, instance, create_time):
        if event_id == '500':
            event = Event(
                event_id = event_id,
                instance_id = instance,
                group = group_name,
                description = description, 
                additional = additional,
                additional2 = additional2,
                additional3 = additional3,
                create_time = create_time
            )
            event.save()

        if event_id in ['101', '102', '103']:
            if event_id == '101' or event_id == '103':
                deploy_status = 'failed'
            elif event_id == '102':
                deploy_status = 'success'
            
            deploy_processes = DeployProcess.objects(deploy_id = additional, instance = instance)
            if not deploy_processes:
                rsp = self.rsp_handler.generate_rsp_msg(22002, None)
                return rsp
            deploy_process = deploy_processes[0]
            deploy_process.result = deploy_status
            deploy_process.end_time = time.strftime('%Y-%m-%d %H:%M:%S')
            deploy_process.save()

        rsp = self.rsp_handler.generate_rsp_msg(200, None)
        return rsp

    def all_event(self):
        events = Event.objects().order_by('create_time')
        event_instances = json.loads(events.to_json())
        rsp_body = {'rsp_body': {'events': event_instances}}
        rsp = self.rsp_handler.generate_rsp_msg(200, rsp_body)
        return rsp

    def get_event(self, event_id, instance_id, group, create_time):
        events = Event.objects(event_id = event_id, instance_id = instance_id, group = group, create_time = create_time)
        if not events:
            rsp = self.rsp_handler.generate_rsp_msg(22002, None)
            return rsp
        event = events[0]
        event_instance = json.loads(event.to_json())
        rsp_body = {'rsp_body': {'event': event_instance}}
        rsp = self.rsp_handler.generate_rsp_msg(200, rsp_body)
        return rsp
        
    def get_current_version(self, env):
        if not env:
            rsp = self.rsp_handler.generate_rsp_msg(29001, None)
            return rsp

        group_instances = []
        datacenters = Datacenter.objects(env = env)
        for datacenter in datacenters:
            groups = DeployGroup.objects(datacenter = datacenter.name).order_by('name')
            for group in groups:
                packages = Package.objects(service = group.service, version = group.version)
                package_status = 'waiting'
                if packages:
                    package = packages[0]
                    if env == 'test':
                        package_status = package.testing if package.testing else 'waiting'
                group_instance = json.loads(group.to_json())
                group_instance['package_status'] = package_status
                group_instances.append(group_instance)

        self.LOG.debug('group_instances is {0}'.format(group_instances))
        rsp_body = {
            'rsp_body': {
                'groups': group_instances 
            }
        }
        rsp = self.rsp_handler.generate_rsp_msg(200, rsp_body)
        return rsp

    def modify_package_status(self, service, version, status):
        if not service or not version or not status:
            rsp = self.rsp_handler.generate_rsp_msg(29001, None)
            return rsp

        packages = Package.objects(service = service, version = version)
        if not packages:
            rsp = self.rsp_handler.generate_rsp_msg(24002, None)
            return rsp

        package = packages[0]
        package.testing = status
        package.save()

        rsp = self.rsp_handler.generate_rsp_msg(200, None)
        return rsp
