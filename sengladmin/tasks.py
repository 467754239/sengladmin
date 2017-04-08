#!/usr/bin/python
#-*-coding:utf-8-*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
# copyright 2015 Sengled, Inc.
# All Rights Reserved.

# @author: WShuai, Sengled, Inc.

from celery import task,platforms
from celery.utils.log import get_task_logger
platforms.C_FORCE_ROOT = True

from django.conf import settings
from django.core.mail import send_mail

import os
import time
import json

from service import commConsul
from service import commAws
from service import commFile
from service import commDeploy
from models import Datacenter,Package,DeployGroup,Consignee,User

logger = get_task_logger(__name__)

@task()
def consul_sync_datacenter(*args, **kwargs):
    datacenter_domain = str(args[0]['qurom']['domain'])
    datacenter_port = int(args[0]['qurom']['port'])
    datacenter_cakey = args[0]['qurom']['cakey']
    datacenter_cacert = args[0]['qurom']['cacert']
    consul_handler = commConsul.CommConsul(datacenter_cacert, datacenter_cakey, LOG = logger)
    consul_handler.connect(datacenter_domain, datacenter_port)

    consul_key = 'deploy/dcInfo'
    consul_value = json.dumps(
        {
            'name': args[0]['name'],
            'envType': args[0]['env'],
            'deployRegion': args[0]['deploy']['region'],
            'deployBucket': args[0]['deploy']['bucket']
        }
    )
    consul_handler.put_values(consul_key, consul_value)

    consul_key = 'deploy/agent/version'
    consul_value = json.dumps(
        {
            'version': args[0]['agent']['version'],
            'file_path': args[0]['agent']['file_path']
        }
    )
    consul_handler.put_values(consul_key, consul_value)
    
    consul_key = 'deploy/agent/authorization'
    consul_value = json.dumps(
        {
            'access_key': args[0]['agent']['secret_access_key'],
            'access_id': args[0]['agent']['access_key_id']
        }
    )
    consul_handler.put_values(consul_key, consul_value)

    consul_handler.clear_consul_cert()
    return

@task()
def consul_add_group(*args, **kwargs):
    group_name = args[0]['name']
    datacenter_name = args[0]['datacenter']

    datacenters = Datacenter.objects(name = datacenter_name)
    if not datacenters:
        logger.error('datacenter not exist.')
        return
    datacenter = datacenters[0]

    packages = Package.objects(service = args[0]['service'], version = args[0]['version'])
    if not packages:
        logger.error('service not exist.')
        return
    package = packages[0]

    datacenter = datacenters[0]
    consul_handler = commConsul.CommConsul(datacenter.qurom['cacert'], datacenter.qurom['cakey'], LOG = logger)
    consul_handler.connect(datacenter.qurom['domain'], datacenter.qurom['port'])

    consul_key = 'deploy/deployGroup/%s/status' % group_name
    consul_value = json.dumps(
        {
            'service': args[0]['service'],
            'cur_version': args[0]['version'],
            'target_version': args[0]['version'],
            'deploy_id': None,
            'file_path': package['file_path'],
            'verify': package['md5'][datacenter_name] if datacenter_name in package['md5'].keys() else package['md5']['source'],
        }
    )
    consul_handler.put_values(consul_key, consul_value)
    
    consul_handler.clear_consul_cert()
    return

@task()
def consul_remove_datacenter(*args, **kwargs):
    datacenter_domain = str(args[0]['qurom']['domain'])
    datacenter_port = int(args[0]['qurom']['port'])
    datacenter_cakey = args[0]['qurom']['cakey']
    datacenter_cacert = args[0]['qurom']['cacert']

    consul_handler = commConsul.CommConsul(datacenter_cacert, datacenter_cakey, LOG = logger)
    consul_handler.connect(datacenter_domain, datacenter_port)
    consul_key = 'deploy/dcInfo'
    consul_handler.del_values(consul_key)
    consul_key = 'deploy/agent/version'
    consul_handler.del_values(consul_key)
    consul_key = 'deploy/agent/authorization'
    consul_handler.del_values(consul_key)

    consul_handler.clear_consul_cert()
    return

@task()
def consul_sync_health(*args, **kwargs):
    datacenter_domain = kwargs['datacenter']['qurom']['domain']
    datacenter_port = kwargs['datacenter']['qurom']['port']
    datacenter_cakey = kwargs['datacenter']['qurom']['cakey']
    datacenter_cacert = kwargs['datacenter']['qurom']['cacert']
    group_name = kwargs['group_name']
    healths = kwargs['healths']
    logger.debug('xxxxxxxxxxxxxxxxxxx')

    consul_handler = commConsul.CommConsul(datacenter_cacert, datacenter_cakey, LOG = logger)
    consul_handler.connect(datacenter_domain, datacenter_port)

    consul_key = 'deploy/deployGroup/%s/checks' % group_name
    consul_value = json.dumps(healths)
    logger.debug('healths is {0}'.format(consul_value))

    if healths:
        consul_handler.put_values(consul_key, consul_value)
    else:
        consul_handler.del_values(consul_key)

    consul_handler.clear_consul_cert()
    return

@task()
def consul_sync_monitor(*args, **kwargs):
    datacenter_domain = kwargs['datacenter']['qurom']['domain']
    datacenter_port = kwargs['datacenter']['qurom']['port']
    datacenter_cakey = kwargs['datacenter']['qurom']['cakey']
    datacenter_cacert = kwargs['datacenter']['qurom']['cacert']
    group_name = kwargs['group_name']
    monitors = kwargs['monitors']

    consul_handler = commConsul.CommConsul(datacenter_cacert, datacenter_cakey, LOG = logger)
    consul_handler.connect(datacenter_domain, datacenter_port)

    consul_key = 'deploy/deployGroup/%s/monitors' % group_name
    consul_value = json.dumps(monitors)

    if monitors:
        consul_handler.put_values(consul_key, consul_value)
    else:
        consul_handler.del_values(consul_key)

    consul_handler.clear_consul_cert()
    return

@task()
def consul_sync_config(*agrs, **kwargs):
    datacenter_domain = kwargs['datacenter']['qurom']['domain']
    datacenter_port = kwargs['datacenter']['qurom']['port']
    datacenter_cakey = kwargs['datacenter']['qurom']['cakey']
    datacenter_cacert = kwargs['datacenter']['qurom']['cacert']
    group_name = kwargs['group_name']
    config_value = kwargs['config_value']
    config_consul_key = kwargs['config_consul_key']

    consul_handler = commConsul.CommConsul(datacenter_cacert, datacenter_cakey, LOG = logger)
    consul_handler.connect(datacenter_domain, datacenter_port)

    consul_key = 'deploy/deployGroup/%s/config/%s' % (group_name, config_consul_key)
    consul_value = config_value
    consul_handler.put_values(consul_key, consul_value)

    consul_handler.clear_consul_cert()
    return

@task()
def consul_sync_configs(*agrs, **kwargs):
    datacenter = kwargs['datacenter']
    group_name = kwargs['group_name']
    configs = kwargs['configs']
    
    consul_handler = commConsul.CommConsul(datacenter['qurom']['cacert'], datacenter['qurom']['cakey'], LOG = logger)
    consul_handler.connect(datacenter['qurom']['domain'], datacenter['qurom']['port'])

    for config in configs:
        if config['consul_key']:
            consul_key = 'deploy/deployGroup/%s/config/%s' % (group_name, config['consul_key'])
            consul_value = config['value']
            consul_handler.put_values(consul_key, consul_value)

    consul_handler.clear_consul_cert()
    return

@task()
def consul_remove_config(*args, **kwargs):
    datacenter_domain = kwargs['datacenter']['qurom']['domain']
    datacenter_port = kwargs['datacenter']['qurom']['port']
    datacenter_cakey = kwargs['datacenter']['qurom']['cakey']
    datacenter_cacert = kwargs['datacenter']['qurom']['cacert']
    group_name = kwargs['group_name']
    config_name = kwargs['config_name']

    consul_handler = commConsul.CommConsul(datacenter_cacert, datacenter_cakey, LOG = logger)
    consul_handler.connect(datacenter_domain, datacenter_port)

    consul_key = 'deploy/deployGroup/%s/config/%s' % (group_name, config_name)
    consul_handler.del_values(consul_key)

    consul_handler.clear_consul_cert()
    return

@task()
def consul_remove_group(*args, **kwargs):
    datacenter_domain = kwargs['datacenter']['qurom']['domain']
    datacenter_port = kwargs['datacenter']['qurom']['port']
    datacenter_cakey = kwargs['datacenter']['qurom']['cakey']
    datacenter_cacert = kwargs['datacenter']['qurom']['cacert']
    group_name = kwargs['group_name']

    consul_handler = commConsul.CommConsul(datacenter_cacert, datacenter_cakey, LOG = logger)
    consul_handler.connect(datacenter_domain, datacenter_port)

    consul_key = 'deploy/deployGroup/%s' % group_name
    consul_handler.del_values(consul_key)

    consul_handler.clear_consul_cert()
    return

@task()
def pre_process_package(*args, **kwargs):
    package = kwargs['package']

    datacenters = Datacenter.objects(region = package['region'], env = 'dev')
    datacenter = datacenters[0]

    file_name = os.path.basename(package['file_path']).replace('tar.gz', '%s.tar.gz' % package['version'])
    local_file_path = os.path.join(settings.PACKAGE_SAVE_PATH, package['service'], file_name)
    path_name = os.path.dirname(local_file_path)
    if not os.path.exists(path_name):
        os.makedirs(path_name)

    s3_handler = commAws.S3Handler(package['region'], datacenter.agent['access_key_id'], datacenter.agent['secret_access_key'], LOG = logger)
    s3_handler.connect()
    s3_handler.get_file(package['bucket'], package['file_path'], local_file_path)

    service_file = commFile.ServicePackage(
        package,
        local_file_path,
        json.loads(datacenter.to_json()),
        LOG = logger
    )
    if not service_file.audit_md5():
        service_file.set_package_status()
        return
    
    service_file.uncompress()
    #service_file.audit_health()
    service_file.audit_sql()
    service_file.audit_port()
    service_file.audit_config()
    service_file.set_package_status()
    service_file.clear()

    if service_file.md5_status == 'pass' and service_file.sql_status == 'pass' and service_file.endpoint_status == 'pass' and service_file.config_status == 'pass':
        package_deploy(package = package, target_env = 'dev', operator = 'auto')
    return

@task()
def package_deploy(*args, **kwargs):
    package = kwargs['package']
    target_env = kwargs['target_env']
    operator = kwargs['operator']
    datacenter_name = kwargs.get('datacenter_name', None)

    logger.info('deploy begin.....')

    if package['service'] == 'agent':
        if datacenter_name:
            datacenters = Datacenter.objects(name = datacenter_name)
            datacenter = datacenters[0]
            deploy_single_agent(json.loads(datacenters.to_json()), package)
            datacenter['agent']['version'] = package['version']
            datacenter['agent']['file_path'] = package['file_path']
            datacenter.save()
            consul_sync_datacenter(datacenter, logger)
        else:
            datacenters = Datacenter.objects(env = target_env)
            for datacenter in datacenters:
                deploy_single_agent(json.loads(datacenters.to_json()), package) 
                datacenter['agent']['version'] = package['version']
                datacenter['agent']['file_path'] = package['file_path']
                datacenter.save()
                consul_sync_datacenter(datacenter, logger)
    else:
        file_name = os.path.basename(package['file_path']).replace('tar.gz', '%s.tar.gz' % package['version'])
        local_file_path = os.path.join(settings.PACKAGE_SAVE_PATH, package['service'], file_name)
        if datacenter_name:
            datacenters = Datacenter.objects(name = datacenter_name)
            datacenter = datacenters[0]
            deploy_single_service(json.loads(datacenter.to_json()), package, local_file_path, operator)

        else:
            datacenters = Datacenter.objects(env = target_env)
            for datacenter in datacenters:
                deploy_single_service(json.loads(datacenter.to_json()), package, local_file_path, operator)
            
    logger.info('deploy finish')
    return

def deploy_single_agent(datacenter, package):
    s3_handler = commAws.S3Handler(
        datacenter['region'],
        datacenter['agent']['access_key_id'],
        datacenter['agent']['secret_access_key'],
        LOG = logger
    )
    s3_handler.connect()
    s3_handler.put_file(
        datacenter['deploy']['bucket'],
        package['file_path'],
        os.path.join(settings.PACKAGE_SAVE_PATH, package['service'], os.path.basename(package['file_path']).replace('tar.gz', '%s.tar.gz' % package['version']))
    )
    logger.info('xxxxxxxxxxxxxxxxxxxxxxxxx upload s3 finished.')
    return

def deploy_single_service(datacenter, package, local_file_path, operator):
    service_package = commFile.ServicePackage(
        package,
        local_file_path,
        datacenter,
        LOG = logger
    )
    try:
        uploaded = package['upload'][datacenter['name']]
    except:
        uploaded = None

    service_package.uncompress()
    if not uploaded:
        logger.info('package not upload, begin upload package.')
        service_package.process_config()
        uploaded = service_package.set_upload()
    else:
        logger.info('package already upload.')
 
    release_note = service_package.get_release_note()
    logger.debug('generate config file finish, new md5 is {0}'.format(service_package.new_md5))
    
    wait_deploy_groups = []
    groups = DeployGroup.objects(service = package['service'], datacenter = datacenter['name'])
    for group in groups:
        want_healths = service_package.auto_create_health(group.name)
        if want_healths:
            consul_sync_health(datacenter = datacenter, group_name = group.name, healths = want_healths)
        wait_deploy_groups.append(
            {
                'service': package['service'],
                'version': package['version'],
                'file_path': package['file_path'],
                'md5': uploaded,
                'operator': operator,

                'group_name': group.name,
                'deploy_policy_type': group.deploy['type'],
                'deploy_policy_value': group.deploy['value'],

                'env': datacenter['env'],
                'datacenter_name': datacenter['name'],
                'datacenter_cacert': datacenter['qurom']['cacert'],
                'datacenter_cakey': datacenter['qurom']['cakey'],
                'datacenter_domain': datacenter['qurom']['domain'],
                'datacenter_port': datacenter['qurom']['port']
            }
        )
    service_package.clear()
    logger.debug('wait to deploy groups are: [{0}]'.format(','.join([item['group_name'] for item in wait_deploy_groups])))
    
    for wait_deploy_group in wait_deploy_groups:
        deploy_handler = commDeploy.DeployHandler(wait_deploy_group, LOG = logger)
        result, message = deploy_handler.process()
        deploy_mail(
            result = result,
            message = message,
            env = datacenter['env'],
            service = package['service'],
            datacenter_name = datacenter['name'],
            release_note = release_note
        )
    return

@task()
def package_upload(*args, **kwargs):
    package = kwargs['package']
    operator = kwargs['operator']
    datacenter = kwargs['datacenter']

    file_name = os.path.basename(package['file_path']).replace('tar.gz', '%s.tar.gz' % package['version'])
    local_file_path = os.path.join(settings.PACKAGE_SAVE_PATH, package['service'], file_name)
    service_package = commFile.ServicePackage(
        package,
        local_file_path,
        datacenter,
        LOG = logger
    )
    service_package.uncompress()
    service_package.process_config()
    service_package.set_upload()
    service_package.clear()
    return

def deploy_mail(*args, **kwargs):
    release_note = kwargs['release_note']
    result = kwargs['result']
    message = kwargs['message']
    env = kwargs['env']
    service = kwargs['service']
    datacenter_name = kwargs['datacenter_name']
 
    datacenters = Datacenter.objects(name = datacenter_name)
    datacenter = datacenters[0]

    operators = User.objects(role = u'运维').only('account')
    mail_inbox = [user.account for user in operators]
    context = 'Deploy service: {0} to datacenter: {1} env: {2} {3}: {4}.'.format(service, datacenter.region, datacenter.env, 'success' if result else 'failed', message)

    if result:
        # send mail to all operations and relations
        relations = Consignee.objects(group = env, service = service).only('email')
        mail_inbox += [relation.email for relation in relations if relation.email not in mail_inbox]
        context = '{0}\r\n\r\n{1}'.format(context, release_note)

    send_mail(
        settings.MAIL_SUBJECT_DEPLOY,
        context,
        settings.MAIL_OUTBOX,
        mail_inbox,
        fail_silently = False
    )
    return
