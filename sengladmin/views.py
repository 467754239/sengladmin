#!/usr/bin/python
# -*-coding:utf-8-*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
# copyright 2015 Sengled, Inc.
# All Rights Reserved.

# @author: WShuai, Sengled, Inc.

from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect, QueryDict
#from django.views.decorators.csrf import requires_csrf_token
from django.views.decorators.csrf import csrf_exempt

import json
import time
import logging
import inspect
from service import userHandler, sysHandler, opsHandler
from service import commDecorator

logger = logging.getLogger('django')
# Create your views here.

@commDecorator.login_required
@commDecorator.print_log(LOG = logger)
def welcome(request):
    resp_json = {
        #'context': json.dumps(request.session.get('current_permissions', {})),
        'current_permission': json.dumps(request.session.get('current_permissions', {})),
        'user_name': request.session.get('user_name', None),
        'account': request.session.get('user_account', None)
    }
    return render_to_response('sengladmin/welcome.html', resp_json)

@commDecorator.print_log(LOG = logger)
def login(request):
    context = {}
    if request.method == 'POST':
        account = request.POST.get('login_account', None)
        password = request.POST.get('login_password', None)
        uuid = request.POST.get('login_uuid', None)
        user_handler = userHandler.UserHandler(request, logger)
        context = user_handler.login(account, password, uuid)
        if context['rsp_head']['rsp_code'] == 200:
            request.session['current_permissions'] = context['rsp_body']['permissions']
            return HttpResponseRedirect('/sengladmin/user/welcome/')
        else:
            context = context['rsp_head']
            context['rsp_request'] = inspect.stack()[0][3]
            return render_to_response('sengladmin/index.html', {'context': context})
    else:
        info = request.GET.get('info', None)
        request = request.GET.get('request', None)
        try:
            context = json.loads(info)
            context['rsp_request'] = request
        except: 
            context = None
        return render_to_response('sengladmin/index.html', {'context': context})

@commDecorator.print_log(LOG = logger)
def register(request):
    context = {}
    if request.method == 'POST':
        account = request.POST.get('register_account', None)
        password = request.POST.get('register_password', None)
        fullname = request.POST.get('fullname', None)
        phone = request.POST.get('phone', None)
        captcha = request.POST.get('captcha', None)
        user_handler = userHandler.UserHandler(request, logger)
        context = user_handler.register(account, password, fullname, phone, captcha)
        return HttpResponseRedirect('/sengladmin/?request=%s&info=%s#signup' % (inspect.stack()[0][3], json.dumps(context['rsp_head'])))
    else:
        return HttpResponseRedirect('/sengladmin/')

@commDecorator.print_log(LOG = logger)
def captcha(request):
    context = {}
    if request.method == 'GET':
        account = request.GET.get('register_account', None)
        user_handler = userHandler.UserHandler(request, logger)
        context = user_handler.get_captcha(account)
    return HttpResponse(json.dumps(context), content_type="application/json")

@commDecorator.login_required
@commDecorator.print_log(LOG = logger)
def logout(request):
    context = {}
    if request.method == 'POST':
        user_handler = userHandler.UserHandler(request, logger)
        context = user_handler.logout()
    return HttpResponse(json.dumps(context), content_type="application/json")

@commDecorator.login_required
@commDecorator.logging_system
@commDecorator.print_log(LOG = logger)
def password(request):
    context = {}
    if request.method == 'POST':
        account = request.POST.get('account', None)
        old_password = request.POST.get('original_password', None)
        new_password = request.POST.get('new_password', None)
        user_handler = userHandler.UserHandler(request, logger)
        context = user_handler.modify_password(account, old_password, new_password)
    elif request.method == 'DELETE':
        request_delete = QueryDict(request.body)
        account = request_delete.get('account', None)
        user_handler = userHandler.UserHandler(request, logger)
        context = user_handler.reset_password(account)
    return HttpResponse(json.dumps(context), content_type="application/json")

@commDecorator.login_required
@commDecorator.print_log(LOG = logger)
def log(request):
    context = {}
    if request.method == 'GET':
        system_handler = sysHandler.SysHandler(request)
        context = system_handler.all_logs()
    resp_json = {
        'context': context,
        'current_permission': json.dumps(request.session.get('current_permissions', {})),
        'user_name': request.session.get('user_name', None),
        'account': request.session.get('user_account', None)
    }
    return render_to_response('sengladmin/log.html', resp_json)
        

@commDecorator.login_required
@commDecorator.logging_system
@commDecorator.print_log(LOG = logger)
def user(request):
    context = {}
    if request.method == 'GET':
        user_account = request.GET.get('account', None)
        user_handler = userHandler.UserHandler(request, logger)
        if not user_account:
            context = user_handler.all_users()
            resp_json = {
                'context': context,
                'current_permission': json.dumps(request.session.get('current_permissions', {})),
                'user_name': request.session.get('user_name', None),
                'account': request.session.get('user_account', None)
            }
            return render_to_response('sengladmin/user.html', resp_json)
        else:
            context = user_handler.get_user(user_account)
            return HttpResponse(json.dumps(context), content_type="application/json")
             
    elif request.method == 'POST':
        user_handler = userHandler.UserHandler(request, logger)
        context = user_handler.modify_user(
            request.POST.get('user_account', None),
            request.POST.get('user_role', None)
        )
        return HttpResponse(json.dumps(context), content_type="application/json")

@commDecorator.login_required
@commDecorator.logging_system
@commDecorator.print_log(LOG = logger)
def role(request):
    context = {}
    if request.method == 'GET':
        role_name = request.GET.get('role_name', None)
        user_handler = userHandler.UserHandler(request, logger)
        if not role_name:
            context = user_handler.all_roles()
            resp_json = {
                'context': context,
                'current_permission': json.dumps(request.session.get('current_permissions', {})),
                'user_name': request.session.get('user_name', None),
                'account': request.session.get('user_account', None)
            }
            return render_to_response('sengladmin/role.html', resp_json)
        else:
            context = user_handler.get_role(role_name)
            return HttpResponse(json.dumps(context), content_type="application/json")

@commDecorator.login_required
@commDecorator.logging_system
@commDecorator.print_log(LOG = logger)
def role_permission(request):
    context = {}
    if request.method == 'GET':
        role_name = request.GET.get('role_name', None)
        user_handler = userHandler.UserHandler(request, logger)
        context = user_handler.get_role_permission(role_name)
        return HttpResponse(json.dumps(context), content_type="application/json")
    elif request.method == 'POST':
        user_handler = userHandler.UserHandler(request, logger)
        context = user_handler.modify_role_permission(
            request.POST.get('role_name', None),
            request.POST.getlist('permission', None)
        )
        return HttpResponse(json.dumps(context), content_type="application/json")


@commDecorator.login_required
@commDecorator.logging_system
@commDecorator.print_log(LOG = logger)
def permission(request):
    context = {}
    if request.method == 'GET':
        permission_name = request.GET.get('permission_name', None)
        user_handler = userHandler.UserHandler(request, logger)
        if not permission_name:
            context = user_handler.all_permissions()
            resp_json = {
                'context': context,
                'current_permission': json.dumps(request.session.get('current_permissions', {})),
                'user_name': request.session.get('user_name', None),
                'account': request.session.get('user_account', None)
            }
            return render_to_response('sengladmin/permission.html', resp_json)
        else:
            context = user_handler.get_permission(permission_name)
            return HttpResponse(json.dumps(context), content_type="application/json")
    elif request.method == 'PUT':
        request_put = QueryDict(request.body)
        user_handler = userHandler.UserHandler(request, logger)
        context = user_handler.create_permission(
            request_put.get('name', None),
            request_put.get('desc', None),
            request_put.get('url', None),
            request_put.get('superior', None),
        )
        return HttpResponse(json.dumps(context), content_type="application/json")
    elif request.method == 'POST':
        user_handler = userHandler.UserHandler(request, logger)
        context = user_handler.modify_permission(
            request.POST.get('name', None),
            request.POST.get('desc', None),
            request.POST.get('url', None),
            request.POST.get('superior', None),
        )
        return HttpResponse(json.dumps(context), content_type="application/json")
    elif request.method == 'DELETE':
        request_delete = QueryDict(request.body)
        permission_name = request_delete.get('permission_name', None)
        user_handler = userHandler.UserHandler(request, logger)
        context = user_handler.remove_permission(permission_name)
        return HttpResponse(json.dumps(context), content_type="application/json")

@commDecorator.login_required
@commDecorator.logging_system
@commDecorator.print_log(LOG = logger)
def consignee(request):
    context = {}
    if request.method == 'GET':
        consignee_name = request.GET.get('consignee_name', None)
        ops_handler = opsHandler.OpsHandler(request, logger)
        if not consignee_name:
            context = ops_handler.all_consignees()
            resp_json = {
                'context': context,
                'current_permission': json.dumps(request.session.get('current_permissions', {})),
                'user_name': request.session.get('user_name', None),
                'account': request.session.get('user_account', None)
            }
            return render_to_response('sengladmin/consignee.html', resp_json)
        else:
            context = ops_handler.get_consignee(consignee_name)
            return HttpResponse(json.dumps(context), content_type="application/json")
    elif request.method == 'PUT':
        request_put = QueryDict(request.body)
        ops_handler = opsHandler.OpsHandler(request, logger)
        context = ops_handler.create_consignee(
            request_put.get('name', None),
            request_put.get('email', None),
            request_put.getlist('group', None),
            request_put.getlist('service', None)
        )
        return HttpResponse(json.dumps(context), content_type="application/json")
    elif request.method == 'DELETE':
        request_delete = QueryDict(request.body)
        consignee_name = request_delete.get('consignee_name', None)
        ops_handler = opsHandler.OpsHandler(request, logger)
        context = ops_handler.remove_consignee(consignee_name)
        return HttpResponse(json.dumps(context), content_type="application/json")
    elif request.method == 'POST':
        ops_handler = opsHandler.OpsHandler(request, logger)
        context = ops_handler.modify_consignee(
            request.POST.get('name', None),
            request.POST.get('email', None),
            request.POST.getlist('group', None),
            request.POST.getlist('service', None)
        )
        return HttpResponse(json.dumps(context), content_type="application/json")

@commDecorator.login_required
@commDecorator.logging_system
@commDecorator.print_log(LOG = logger)
def datacenter(request):
    context = {}
    if request.method == 'GET':
        datacenter_name = request.GET.get('datacenter_name', None)
        ops_handler = opsHandler.OpsHandler(request, logger)
        if not datacenter_name:
            context = ops_handler.all_datacenters()
            resp_json = {
                'context': context, 
                'current_permission': json.dumps(request.session.get('current_permissions', {})),
                'user_name': request.session.get('user_name', None),
                'account': request.session.get('user_account', None)
            }
            return render_to_response('sengladmin/datacenter.html', resp_json)
        else:
            context = ops_handler.get_datacenter(datacenter_name)
            return HttpResponse(json.dumps(context), content_type="application/json")
    elif request.method == 'DELETE':
        request_delete = QueryDict(request.body)
        authorize_code = request_delete.get('authorize', None)
        datacenter_name = request_delete.get('datacenter_name', None)
        ops_handler = opsHandler.OpsHandler(request, logger)
        context = ops_handler.remove_datacenter(authorize_code, datacenter_name)
        return HttpResponse(json.dumps(context), content_type="application/json")
    elif request.method == 'PUT':
        request_put = QueryDict(request.body)
        ops_handler = opsHandler.OpsHandler(request, logger)
        context = ops_handler.create_datacenter(
            request_put.get('name', None),
            request_put.get('location', None),
            request_put.get('env', None),
            request_put.get('type', None),
            request_put.get('region', None),
            request_put.get('deploy_region', None),
            request_put.get('deploy_bucket', None),
            request_put.get('qurom_domain', None),
            request_put.get('qurom_port', None),
            request_put.get('qurom_cacert', None),
            request_put.get('qurom_cakey', None),
            request_put.get('agent_version', None),
            request_put.get('agent_file_path', None),
            request_put.get('agent_access_key', None),
            request_put.get('agent_secret_access', None) 
        )
        return HttpResponse(json.dumps(context), content_type="application/json")
    elif request.method == 'POST':
        ops_handler = opsHandler.OpsHandler(request, logger)
        context = ops_handler.modify_datacenter(
            request.POST.get('name', None),
            request.POST.get('location', None),
            request.POST.get('env', None),
            request.POST.get('type', None),
            request.POST.get('region', None),
            request.POST.get('deploy_region', None),
            request.POST.get('deploy_bucket', None),
            request.POST.get('qurom_domain', None),
            request.POST.get('qurom_port', None),
            request.POST.get('qurom_cacert', None),
            request.POST.get('qurom_cakey', None),
            request.POST.get('agent_version', None),
            request.POST.get('agent_file_path', None),
            request.POST.get('agent_access_key', None),
            request.POST.get('agent_secret_access', None)
        )
        return HttpResponse(json.dumps(context), content_type="application/json")

@commDecorator.login_required
@commDecorator.logging_system
@commDecorator.print_log(LOG = logger)
def datacenter_status(request):
    context = {}
    if request.method == 'POST':
        name = request.POST.get('name', None)
        status = request.POST.get('status', None)
        ops_handler = opsHandler.OpsHandler(request, logger)
        context = ops_handler.modify_datacenter_status(name, status)
        return HttpResponse(json.dumps(context), content_type="application/json")

@commDecorator.login_required
@commDecorator.print_log(LOG = logger)
def resource(request):
    context = {}
    if request.method == 'GET':
        group_name = request.GET.get('group', None)
        ops_handler = opsHandler.OpsHandler(request, logger)
        context = ops_handler.all_resources(group_name)
        return HttpResponse(json.dumps(context), content_type="application/json")

@commDecorator.login_required
@commDecorator.print_log(LOG = logger)
def resource_condition(request):
    context = {}
    if request.method == 'GET':
        datacenter_name = request.GET.get('datacenter', None)
        service_name = request.GET.get('service', None)
        ops_handler = opsHandler.OpsHandler(request, logger)
        context = ops_handler.condition_resources(datacenter_name, service_name)
        return HttpResponse(json.dumps(context), content_type="application/json")
        
@commDecorator.login_required
@commDecorator.logging_system
@commDecorator.print_log(LOG = logger)
def service(request):
    context = {}
    if request.method == 'GET':
        ops_handler = opsHandler.OpsHandler(request, logger)
        context = ops_handler.all_services()
        resp_json = {
            'context': context, 
            'current_permission': json.dumps(request.session.get('current_permissions', {})),
            'user_name': request.session.get('user_name', None),
            'account': request.session.get('user_account', None)
        }
        return render_to_response('sengladmin/service.html', resp_json)
    elif request.method == 'PUT':
        request_put = QueryDict(request.body)
        ops_handler = opsHandler.OpsHandler(request, logger)
        context = ops_handler.create_service(
            request_put.get('name', None),
            request_put.get('description', None),
            request_put.get('git_path', None),
            #request_put.get('build_env_type', None),
            #request_put.get('build_env_value', None),
            request_put.get('build_trigger', None),
            request_put.get('build_trigger_str', None)
        )
        return HttpResponse(json.dumps(context), content_type="application/json")
    elif request.method == 'DELETE':
        request_delete = QueryDict(request.body)
        service_name = request_delete.get('name', None)
        ops_handler = opsHandler.OpsHandler(request, logger)
        context = ops_handler.remove_service(service_name)
        return HttpResponse(json.dumps(context), content_type="application/json")

@commDecorator.login_required
@commDecorator.logging_system
@commDecorator.print_log(LOG = logger)
def service_status(request):
    context = {}
    if request.method == 'POST':
        name = request.POST.get('name', None)
        status = request.POST.get('status', None)
        ops_handler = opsHandler.OpsHandler(request, logger)
        context = ops_handler.modify_service_status(name, status)
        return HttpResponse(json.dumps(context), content_type="application/json")

@commDecorator.login_required
@commDecorator.logging_system
@commDecorator.print_log(LOG = logger)
def group(request):
    context = {}
    if request.method == 'GET':
        group_name = request.GET.get('group_name', None)
        group_datacenter = request.GET.get('sel_group_datacenter', None)
        ops_handler = opsHandler.OpsHandler(request, logger)
        if not group_name:
            context = ops_handler.all_groups(group_datacenter)
            resources = ops_handler.all_datacenters()
            resp_json = {
                'context': context, 
                'resources': json.dumps(resources),
                'current_permission': json.dumps(request.session.get('current_permissions', {})),
                'user_name': request.session.get('user_name', None),
                'account': request.session.get('user_account', None)
            }
            return render_to_response('sengladmin/group.html', resp_json)
        else:
            context = ops_handler.get_group(group_name)
            return HttpResponse(json.dumps(context), content_type="application/json")
    elif request.method == 'PUT':
        request_put = QueryDict(request.body)
        ops_handler = opsHandler.OpsHandler(request, logger)
        context = ops_handler.create_group(
            request_put.get('name', None),
            request_put.get('service', None),
            request_put.get('version', None),
            request_put.get('datacenter', None),
            request_put.get('rm_type', None),
            request_put.get('rm_name', None),
            request_put.get('deploy_type', None),
            request_put.get('deploy_value', 0)
        )
        return HttpResponse(json.dumps(context), content_type="application/json")
    elif request.method == 'POST':
        ops_handler = opsHandler.OpsHandler(request, logger)
        context = ops_handler.modify_group(
            request.POST.get('name', None),
            request.POST.get('rm_type', None),
            request.POST.get('rm_name', None),
            request.POST.get('deploy_type', None),
            request.POST.get('deploy_value', None),
        )
        return HttpResponse(json.dumps(context), content_type="application/json")
    elif request.method == 'DELETE':
        request_delete = QueryDict(request.body)
        authorize_code = request_delete.get('authorize', None)
        group_name = request_delete.get('name', None)
        ops_handler = opsHandler.OpsHandler(request, logger)
        context = ops_handler.remove_group(authorize_code, group_name)
        return HttpResponse(json.dumps(context), content_type="application/json")

@commDecorator.login_required
@commDecorator.logging_system
@commDecorator.print_log(LOG = logger)
def config(request):
    context = {}
    if request.method == 'GET':
        config_key = request.GET.get('key', None)
        config_datacenter = request.GET.get('sel_config_datacenter', None)
        config_domain = request.GET.get('sel_config_domain', None)
        ops_handler = opsHandler.OpsHandler(request, logger)
        if not config_key:
            context = ops_handler.all_configs(config_datacenter, config_domain)
            resources = ops_handler.all_resources()
            resp_json = {
                'context': context,
                'resources': json.dumps(resources),
                'current_permission': json.dumps(request.session.get('current_permissions', {})),
                'user_name': request.session.get('user_name', None),
                'account': request.session.get('user_account', None)
            }
            return render_to_response('sengladmin/config.html', resp_json)
        else:
            config_datacenter = request.GET.get('datacenter', None)
            config_domain = request.GET.get('domain', None)
            context = ops_handler.get_config(config_key, config_datacenter, config_domain)
            return HttpResponse(json.dumps(context), content_type="application/json")
    elif request.method == 'PUT':
        request_put = QueryDict(request.body)
        ops_handler = opsHandler.OpsHandler(request, logger)
        context = ops_handler.create_config(
            request_put.get('key', None),
            request_put.get('description', None),
            request_put.get('value', None),
            request_put.get('consul_key', None),
            request_put.get('consul_value', None),
            request_put.get('datacenter', None),
            request_put.get('domain', None)
        )
        return HttpResponse(json.dumps(context), content_type="application/json")
    elif request.method == 'POST':
        ops_handler = opsHandler.OpsHandler(request, logger)
        context = ops_handler.modify_config(
            request.POST.get('key', None),
            request.POST.get('description', None),
            request.POST.get('value', None),
            request.POST.get('consul_value', None),
            request.POST.get('datacenter', None),
            request.POST.get('domain', None)
        )
        return HttpResponse(json.dumps(context), content_type="application/json")
    elif request.method == 'DELETE':
        request_delete = QueryDict(request.body)
        ops_handler = opsHandler.OpsHandler(request, logger)
        context = ops_handler.remove_config(
            request_delete.get('key', None),
            request_delete.get('datacenter', None),
            request_delete.get('domain', None)
        )
        return HttpResponse(json.dumps(context), content_type="application/json") 

@commDecorator.login_required
@commDecorator.logging_system
@commDecorator.print_log(LOG = logger)
def consul_datacenter(request):
    context = {}
    if request.method == 'POST':
        name = request.POST.get('name', None)
        ops_handler = opsHandler.OpsHandler(request, logger)
        context = ops_handler.sync_datacenter(name)
        return HttpResponse(json.dumps(context), content_type="application/json") 

@commDecorator.login_required
@commDecorator.logging_system
@commDecorator.print_log(LOG = logger)
def consul_health(request):
    context = {}
    if request.method == 'POST':
        group_name = request.POST.get('group', None)
        health_names = request.POST.get('healths', None).split(',')
        ops_handler = opsHandler.OpsHandler(request, logger)
        context = ops_handler.sync_health(group_name, health_names)
        return HttpResponse(json.dumps(context), content_type="application/json") 

@commDecorator.login_required
@commDecorator.logging_system
@commDecorator.print_log(LOG = logger)
def consul_monitor(request):
    context = {}
    if request.method == 'POST':
        group_name = request.POST.get('group', None)
        monitor_names = request.POST.get('monitors', None).split(',')
        ops_handler = opsHandler.OpsHandler(request, logger)
        context = ops_handler.sync_monitor(group_name, monitor_names)
        return HttpResponse(json.dumps(context), content_type="application/json") 

@commDecorator.login_required
@commDecorator.logging_system
@commDecorator.print_log(LOG = logger)
def consul_config(request):
    context = {}
    if request.method == 'POST':
        group_name = request.POST.get('name', None)
        ops_handler = opsHandler.OpsHandler(request, logger)
        context = ops_handler.sync_config(group_name)
        return HttpResponse(json.dumps(context), content_type="application/json") 

@commDecorator.login_required
@commDecorator.logging_system
@commDecorator.print_log(LOG = logger)
def health(request):
    context = {}
    if request.method == 'GET':
        health_name = request.GET.get('health_name', None)
        ops_handler = opsHandler.OpsHandler(request, logger)
        if not health_name:
            context = ops_handler.all_healths()
            resp_json = {
                'context': context,
                'current_permission': json.dumps(request.session.get('current_permissions', {})),
                'user_name': request.session.get('user_name', None),
                'account': request.session.get('user_account', None)
            }
            return render_to_response('sengladmin/health.html', resp_json)
        else:
            context = ops_handler.get_health(health_name)
            return HttpResponse(json.dumps(context), content_type="application/json")
    elif request.method == 'PUT':
        request_put = QueryDict(request.body)
        ops_handler = opsHandler.OpsHandler(request, logger)
        context = ops_handler.create_health(
            request_put.get('name', None),
            request_put.get('type', None),
            request_put.get('value', None),
            request_put.get('interval', 0),
            request_put.get('timeout', 0),
            request_put.get('pending', 0),
            request_put.get('healthy_threshold', 0),
            request_put.get('unhealthy_threshold', 0),
            request_put.get('failback', None)
        )
        return HttpResponse(json.dumps(context), content_type="application/json")
    elif request.method == 'POST':
        ops_handler = opsHandler.OpsHandler(request, logger)
        context = ops_handler.modify_health(
            request.POST.get('name', None),
            request.POST.get('type', None),
            request.POST.get('value', None),
            request.POST.get('interval', 0),
            request.POST.get('timeout', 0),
            request.POST.get('pending', 0),
            request.POST.get('healthy_threshold', 0),
            request.POST.get('unhealthy_threshold', 0),
            request.POST.get('failback', None)
        )
        return HttpResponse(json.dumps(context), content_type="application/json")
    elif request.method == 'DELETE':
        request_delete = QueryDict(request.body)
        health_name = request_delete.get('name', None)
        ops_handler = opsHandler.OpsHandler(request, logger)
        context = ops_handler.remove_health(health_name)
        return HttpResponse(json.dumps(context), content_type="application/json")

@commDecorator.login_required
@commDecorator.logging_system
@commDecorator.print_log(LOG = logger)
def monitor(request):
    context = {}
    if request.method == 'GET':
        monitor_name = request.GET.get('monitor_name', None)
        ops_handler = opsHandler.OpsHandler(request, logger)
        if not monitor_name:
            context = ops_handler.all_monitors()
            resp_json = {
                'context': context,
                'current_permission': json.dumps(request.session.get('current_permissions', {})),
                'user_name': request.session.get('user_name', None),
                'account': request.session.get('user_account', None)
            }
            return render_to_response('sengladmin/monitor.html', resp_json)
        else:
            context = ops_handler.get_monitor(monitor_name)
            return HttpResponse(json.dumps(context), content_type="application/json")
    elif request.method == 'PUT':
        request_put = QueryDict(request.body)
        ops_handler = opsHandler.OpsHandler(request, logger)
        context = ops_handler.create_monitor(
            request_put.get('name', None),
            request_put.get('type', None),
            request_put.get('value', None)
        )
        return HttpResponse(json.dumps(context), content_type="application/json")
    elif request.method == 'POST':
        ops_handler = opsHandler.OpsHandler(request, logger)
        context = ops_handler.modify_monitor(
            request.POST.get('name', None),
            request.POST.get('type', None),
            request.POST.get('value', None)
        )
        return HttpResponse(json.dumps(context), content_type="application/json")
    elif request.method == 'DELETE':
        request_delete = QueryDict(request.body)
        monitor_name = request_delete.get('name', None)
        ops_handler = opsHandler.OpsHandler(request, logger)
        context = ops_handler.remove_monitor(monitor_name)
        return HttpResponse(json.dumps(context), content_type="application/json")


#@commDecorator.login_required
@commDecorator.logging_system
@commDecorator.print_log(LOG = logger)
def package(request):
    context = {}
    if request.method == 'GET':
        package_service = request.GET.get('service', None)
        package_version = request.GET.get('version', None)
        ops_handler = opsHandler.OpsHandler(request, logger)
        if not package_service or not package_version:
            context = ops_handler.all_packages()
            resp_json = {
                'context': context,
                'current_permission': json.dumps(request.session.get('current_permissions', {})),
                'user_name': request.session.get('user_name', None),
                'account': request.session.get('user_account', None)
            }
            return render_to_response('sengladmin/package.html', resp_json)
        else:
            context = ops_handler.get_package(package_service, package_version)
            return HttpResponse(json.dumps(context), content_type="application/json")
    elif request.method == 'PUT':
        request_put = QueryDict(request.body)
        ops_handler = opsHandler.OpsHandler(request, logger)
        context = ops_handler.create_package(
            request_put.get('service', None),
            request_put.get('version', None),
            request_put.get('md5', None),
            request_put.get('region', None),
            request_put.get('bucket', None),
            request_put.get('file_path', None)
        )
        return HttpResponse(json.dumps(context), content_type="application/json")
    elif request.method == 'DELETE':
        request_delete = QueryDict(request.body)
        authorize_code = request_delete.get('authorize', None)
        package_service = request_delete.get('service', None)
        package_version = request_delete.get('version', None)
        ops_handler = opsHandler.OpsHandler(request, logger)
        context = ops_handler.remove_package(authorize_code, package_service, package_version)
        return HttpResponse(json.dumps(context), content_type="application/json")

@commDecorator.login_required
@commDecorator.logging_system
@commDecorator.print_log(LOG = logger)
def audit(request):
    context = {}
    if request.method == 'GET':
        package_service = request.GET.get('service', None)
        package_version = request.GET.get('version', None)
        ops_handler = opsHandler.OpsHandler(request, logger)
        if not package_service or not package_version:
            context = ops_handler.all_packages()
            package_type = '全部版本包列表'
            resp_json = {
                'context': context,
                'current_permission': json.dumps(request.session.get('current_permissions', {})),
                'package_type': package_type,
                'user_name': request.session.get('user_name', None),
                'account': request.session.get('user_account', None)
            }
            return render_to_response('sengladmin/audit.html', resp_json)
        else:
            context = ops_handler.get_audit(package_service, package_version)
            return HttpResponse(json.dumps(context), content_type="application/json")
    elif request.method == 'POST':
        authorize = request.POST.get('authorize', None)
        service = request.POST.get('service', None)
        version = request.POST.get('version', None)
        type = request.POST.get('type', None)
        status = request.POST.get('status', None)
        ops_handler = opsHandler.OpsHandler(request, logger)
        context = ops_handler.audit(
            request.session.get('user_account', None),
            authorize,
            service,
            version,
            type,
            status
        )
        return HttpResponse(json.dumps(context), content_type="application/json")

@commDecorator.login_required
@commDecorator.logging_system
@commDecorator.print_log(LOG = logger)
def audit_sub(request):
    context = {}
    if request.method == 'GET':
        status = request.GET.get('status', None)
        ops_handler = opsHandler.OpsHandler(request, logger)
        context = ops_handler.get_audit_sub(status)
        if status == 'wait':
            package_type = '等待审核版本包列表'
        elif status == 'pass':
            package_type = '审核通过版本包列表'
        elif status == 'refuse':
            package_type = '审核拒绝版本包列表'
        else:
            package_type = '全部版本包列表'
        resp_json = {
            'package_type': package_type,
            'current_permission': json.dumps(request.session.get('current_permissions', {})),
            'context': context,
            'user_name': request.session.get('user_name', None),
            'account': request.session.get('user_account', None)
        }
        return render_to_response('sengladmin/audit.html', resp_json)

@commDecorator.login_required
@commDecorator.logging_system
@commDecorator.print_log(LOG = logger)
def audit_force(request):
    context = {}
    if request.method == 'POST':
        authorize = request.POST.get('authorize', None)
        service = request.POST.get('service', None)
        version = request.POST.get('version', None)
        ops_handler = opsHandler.OpsHandler(request, logger)
        context = ops_handler.audit_force(authorize, service, version)
        return HttpResponse(json.dumps(context), content_type="application/json")

@commDecorator.login_required
@commDecorator.logging_system
@commDecorator.print_log(LOG = logger)
def deploy_operator(request):
    context = {}
    if request.method == 'GET':
        ops_handler = opsHandler.OpsHandler(request, logger)
        context = ops_handler.all_resources()
        resp_json = {
            'context': json.dumps(context),
            'current_permission': json.dumps(request.session.get('current_permissions', {})),
            'user_name': request.session.get('user_name', None),
            'account': request.session.get('user_account', None)
        }
        return render_to_response('sengladmin/deploy_operator.html', resp_json)
    elif request.method == 'POST':
        ops_handler = opsHandler.OpsHandler(request, logger)
        context = ops_handler.deploy(
            request.POST.get('datacenter_name', None),
            request.POST.get('service_name', None),
            request.POST.get('group_name', None),
            request.POST.get('version', None),
            request.session.get('user_name', None),
        )
        return HttpResponse(json.dumps(context), content_type="application/json") 

@commDecorator.login_required
@commDecorator.logging_system
@commDecorator.print_log(LOG = logger)
def deploy_record(request):
    context = {}
    if request.method == 'GET':
        deploy_id = request.GET.get('deploy_id', None)
        ops_handler = opsHandler.OpsHandler(request, logger)
        if not deploy_id:
            context = ops_handler.all_deploy_record()
            resp_json = {
                'context': context,
                'current_permission': json.dumps(request.session.get('current_permissions', {})),
                'user_name': request.session.get('user_name', None),
                'account': request.session.get('user_account', None)
            }
            return render_to_response('sengladmin/deploy_record.html', resp_json)
        else:
            context = ops_handler.get_deploy_record(deploy_id)
            return HttpResponse(json.dumps(context), content_type="application/json")
            
@commDecorator.login_required
@commDecorator.logging_system
@commDecorator.print_log(LOG = logger)
def deploy_process(request):
    context = {}
    if request.method == 'GET':
        ops_handler = opsHandler.OpsHandler(request, logger)                                                            
        context = ops_handler.all_deploy_process()
        resp_json = {
            'context': context,
            'current_permission': json.dumps(request.session.get('current_permissions', {})),
            'user_name': request.session.get('user_name', None),
            'account': request.session.get('user_account', None)
        }
        return render_to_response('sengladmin/deploy_process.html', resp_json)
    elif request.method == 'POST':
        deploy_id = request.POST.get('deploy_id', None)
        deploy_ip = request.POST.get('instance', None)
        deploy_status = request.POST.get('status', None)
        ops_handler = opsHandler.OpsHandler(request, logger)
        context = ops_handler.modify_deploy_process(deploy_id, deploy_ip, deploy_status)
        return HttpResponse(json.dumps(context), content_type="application/json")

@commDecorator.print_log(LOG = logger)
def agent_event(request):
    context = {}
    if request.method == 'POST':
        logger.debug(request.POST)
        event_id = request.POST.get('eventID', None)
        ops_handler = opsHandler.OpsHandler(request, logger)
        context = ops_handler.create_event(
            request.POST.get('eventID', None),
            request.POST.get('description', None),
            request.POST.get('additional', None),
            request.POST.get('additional2', None),
            request.POST.get('additional3', None),
            request.POST.get('deploygroup', None),
            request.POST.get('instanceID', None),
            request.POST.get('create_time', None)
        )
        return HttpResponse(json.dumps(context), content_type="application/json")

@commDecorator.login_required
@commDecorator.logging_system
@commDecorator.print_log(LOG = logger)
def event(request):
    context = {}
    if request.method == 'GET':
        event_id = request.GET.get('event_id', None)
        ops_handler = opsHandler.OpsHandler(request, logger)
        if not event_id:
            context = ops_handler.all_event()
            resp_json = {
                'context': context,
                'current_permission': json.dumps(request.session.get('current_permissions', {})),
                'user_name': request.session.get('user_name', None),
                'account': request.session.get('user_account', None)
            }
            return render_to_response('sengladmin/event.html', resp_json)
        else:
            context = ops_handler.get_event(
                request.GET.get('event_id', None),
                request.GET.get('instance_id', None),
                request.GET.get('group', None),
                request.GET.get('create_time', None)
            )
            print context
            return HttpResponse(json.dumps(context), content_type="application/json")

@commDecorator.login_required
@commDecorator.logging_system
@commDecorator.print_log(LOG = logger)
def testing(request):
    context = {}
    if request.method == 'GET':
        ops_handler = opsHandler.OpsHandler(request, logger)
        context = ops_handler.get_current_version('test')
        resp_json = {
            'context': context,
            'current_permission': json.dumps(request.session.get('current_permissions', {})),
            'user_name': request.session.get('user_name', None),
            'account': request.session.get('user_account', None)
        }
        return render_to_response('sengladmin/testing.html', resp_json)
    elif request.method == 'POST':
        ops_handler = opsHandler.OpsHandler(request, logger)
        context = ops_handler.modify_package_status(
            request.POST.get('service', None),
            request.POST.get('version', None),
            request.POST.get('status', None)
        )
        return HttpResponse(json.dumps(context), content_type="application/json")

@commDecorator.login_required
@commDecorator.logging_system
@commDecorator.print_log(LOG = logger)
def develop_service(request):
    context = {}
    if request.method == 'GET':
        service_name = request.GET.get('service_name', None)
        ops_handler = opsHandler.OpsHandler(request, logger)
        if not service_name:
            context = ops_handler.all_services()
            resp_json = {
                'context': context,
                'current_permission': json.dumps(request.session.get('current_permissions', {})),
                'user_name': request.session.get('user_name', None),
                'account': request.session.get('user_account', None)
            }
            return render_to_response('sengladmin/develop_service.html', resp_json)
        else:
            context = ops_handler.get_service(service_name)
            return HttpResponse(json.dumps(context), content_type="application/json")
    elif request.method == 'PUT':
        request_put = QueryDict(request.body)
        ops_handler = opsHandler.OpsHandler(request, logger)
        context = ops_handler.create_service(
            request_put.get('name', None),
            request_put.get('description', None),
            request_put.get('git_path', None),
            #request_put.get('build_env_type', None),
            #request_put.get('build_env_value', None),
            request_put.get('build_trigger', None),
            request_put.get('build_trigger_str', None),
            request_put.get('build_docker_image_id', None),
        )
        return HttpResponse(json.dumps(context), content_type="application/json")
    elif request.method == 'POST':
        print request.POST
        ops_handler = opsHandler.OpsHandler(request, logger)
        context = ops_handler.modify_service(
            request.POST.get('name', None),
            request.POST.get('description', None),
            request.POST.get('git_path', None),
            #request.POST.get('build_env_type', None),
            #request.POST.get('build_env_value', None),
            request.POST.get('build_trigger', None),
            request.POST.get('build_trigger_str', None),
            request.POST.get('build_docker_image_id', None),
        )
        return HttpResponse(json.dumps(context), content_type="application/json")

@commDecorator.login_required
@commDecorator.logging_system
@commDecorator.print_log(LOG = logger)
def develop_config(request):
    context = {}
    if request.method == 'GET':
        config_key = request.GET.get('key', None)
        config_datacenter = request.GET.get('sel_config_datacenter', None)
        config_domain = request.GET.get('sel_config_domain', None)
        ops_handler = opsHandler.OpsHandler(request, logger)
        if not config_key:
            context = ops_handler.all_configs(config_datacenter, config_domain)
            resources = ops_handler.all_resources()
            resp_json = {
                'context': context,
                'resources': json.dumps(resources),
                'current_permission': json.dumps(request.session.get('current_permissions', {})),
                'user_name': request.session.get('user_name', None),
                'account': request.session.get('user_account', None)
            }
            return render_to_response('sengladmin/develop_config.html', resp_json)
        else:
            config_datacenter = request.GET.get('datacenter', None)
            config_domain = request.GET.get('domain', None)
            context = ops_handler.get_config(config_key, config_datacenter, config_domain)
            return HttpResponse(json.dumps(context), content_type="application/json")

@commDecorator.login_required
@commDecorator.logging_system
@commDecorator.print_log(LOG = logger)
def develop_version(request):
    context = {}
    if request.method == 'GET':
        ops_handler = opsHandler.OpsHandler(request, logger)
        context = ops_handler.get_current_version('dev')
        resp_json = {
            'context': context,
            'current_permission': json.dumps(request.session.get('current_permissions', {})),
            'user_name': request.session.get('user_name', None),
            'account': request.session.get('user_account', None)
        }
        return render_to_response('sengladmin/develop_version.html', resp_json)

