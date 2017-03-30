#!/usr/bin/python
# vim: tabstop=4 shiftwidth=4 softtabstop=4
#-*-coding:utf-8-*-
# copyright 2015 Sengled, Inc.
# All Rights Reserved.

# @author: WShuai, Sengled, Inc.

from django.views.decorators.csrf import requires_csrf_token

import time
import json
from sengladmin.models import Syslog
from commResponse import CommResponse

class SysHandler(object):
    def __init__(self, request):
        self.request = request
        self.rsp_handler = CommResponse()
        return

    def all_logs(self):
        logs = Syslog.objects.exclude('id').order_by('-time')
        log_instances = json.loads(logs.to_json())
        rsp_body = {'rsp_body': {'logs': log_instances}}
        rsp = self.rsp_handler.generate_rsp_msg(200, rsp_body)
        return rsp
