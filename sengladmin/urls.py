from django.conf.urls import url
from django.views.generic.base import RedirectView

from . import views

urlpatterns = [
    url(r'^$', views.login, name='login'),

    url(r'^user/$', views.user, name = 'user'),
    url(r'^user/register/$', views.register, name = 'register'),
    url(r'^user/captcha/$', views.captcha, name = 'captcha'),
    url(r'^user/welcome/$', views.welcome, name = 'welcome'),
    url(r'^user/password/$', views.password, name = 'password'),
    url(r'^user/logout/$', views.logout, name = 'logout'),
    url(r'^role/$', views.role, name = 'role'),
    url(r'^role/permission/$', views.role_permission, name = 'role_permission'),
    url(r'^permission/$', views.permission, name = 'permission'),
    url(r'^log/$', views.log, name = 'log'),

    url(r'^datacenter/$', views.datacenter, name = 'datacenter'),
    url(r'^datacenter/status/$', views.datacenter_status, name = 'datacenter_status'),
    url(r'^service/$', views.service, name = 'service'),
    url(r'^service/status/$', views.service_status, name = 'service_status'),
    url(r'^group/$', views.group, name = 'group'),
    url(r'^health/$', views.health, name = 'health'),
    url(r'^monitor/$', views.monitor, name = 'monitor'),
    url(r'^config/$', views.config, name = 'config'),
    url(r'^package/$', views.package, name = 'package'),
   
    url(r'^audit/$', views.audit, name = 'audit'),
    url(r'^audit/sub/$', views.audit_sub, name = 'audit_sub'),
    url(r'^audit/force/$', views.audit_force, name = 'audit_force'),
    url(r'^resource/$', views.resource, name = 'resource'),
    url(r'^resource/condition/$', views.resource_condition, name = 'resource_condition'),
    url(r'^consul/datacenter/$', views.consul_datacenter, name = 'consul_datacenter'),
    url(r'^consul/health/$', views.consul_health, name = 'consul_health'),
    url(r'^consul/monitor/$', views.consul_monitor, name = 'consul_monitor'),
    url(r'^consul/config/$', views.consul_config, name = 'consul_config'),

    url(r'^deploy/$', views.deploy_operator, name = 'deploy_operator'),
    url(r'^deploy/record/$', views.deploy_record, name = 'deploy_record'),
    url(r'^deploy/process/$', views.deploy_process, name = 'deploy_process'),
    url(r'^deploy/upload/$', views.deploy_upload, name = 'deploy_upload'),
    url(r'^agent/event/$', views.agent_event, name = 'agent_event'),

    url(r'^consignee/$', views.consignee, name = 'consignee'),
    url(r'^event/$', views.event, name = 'event'),

    url(r'^testing/$', views.testing, name = 'testing'),

    url(r'^develop/service/$', views.develop_service, name = 'develop_service'),
    url(r'^develop/config/$', views.develop_config, name = 'develop_config'),
    url(r'^develop/version/$', views.develop_version, name = 'develop_version'),
]
