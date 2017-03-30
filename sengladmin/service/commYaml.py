#!/usr/bin/python
# -*- coding:utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
# copyright 2016 Wshuai, Inc.
# All Rights Reserved.

# @author: WShuai, Wshuai, Inc.

import yaml

class YamlHandler(object):
    def __init__(self, file, LOG):
        self.file = file
        self.yaml_content = None
        self.LOG = LOG
        return

    def load(self):
        try:
            with open(self.file) as file_handler:
                self.yaml_content = yaml.load(file_handler)
            return True
        except Exception as e:
            self.LOG.error('open yaml file {0} failed: {1}'.format(self.file, e))
            return False

    def process_execenv(self):
        return

    def process_endpoint(self):
        want_endpoint = {}
        for endpoint in self.yaml_content['exec']:
            want_endpoint[endpoint['port']] = endpoint['type']
        return want_endpoint

    def process_health(self):
        want_healths = []
        for healths in self.yaml_content['exec']:
            want_healths.append(healths)
        return want_healths
