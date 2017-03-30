#!/usr/bin/python
# -*-coding:utf-8-*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
# copyright 2016 Wshuai, Inc.
# All Rights Reserved.

# @author: WShuai, Wshuai, Inc.

import time
from django.conf import settings
from django.core.cache import cache
from django.shortcuts import resolve_url
from django.contrib.auth.views import redirect_to_login

from sengladmin.models import Syslog

from functools import wraps

def login_required(function = None, redirect_field_name = None, login_url=None):
    def _login_required(request, *args, **kwargs):
        if not request.session.get('user_uuid', default = None):
            path = request.build_absolute_uri()
            resolved_login_url = resolve_url(login_url or settings.LOGIN_URL)
            return redirect_to_login(path, resolved_login_url, redirect_field_name)
        else:
            return function(request, *args, **kwargs)
    return _login_required

def logging_system(function):
    def _logging_system(request, *args, **kwargs):
        now_time = time.strftime('%Y-%m-%d %H:%M:%S')
        operation = request.method + ' ' + request.path
        user_name = request.session.get('user_name', 'auto')
        if request.META.has_key('HTTP_X_FORWARDED_FOR'):  
            client_addr =  request.META['HTTP_X_FORWARDED_FOR']  
        else:  
            client_addr = request.META['REMOTE_ADDR']
        syslog = Syslog(time = now_time, operation = operation, user = user_name, addr = client_addr)
        syslog.save()
        return function(request, *args, **kwargs)
    return _logging_system

def print_log(function = None, LOG = None):
    def decorator(function):
        @wraps(function)
        def _print_log(request, *args, **kwargs):
            LOG.info('{0} {1}'.format(request.method, request.path))
            return function(request, *args, **kwargs)
        return _print_log
    return decorator
