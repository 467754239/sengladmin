#!/usr/bin/python
# -*-coding:utf-8-*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
# copyright 2017 Sengled, Inc.
# All Rights Reserved.

# @author: WShuai, Sengled, Inc.

import jenkins

class JenkinsHandler(object):
    def __init__(self, host, port, user, pswd):
        self.jenkins_host = host
        self.jenkins_port = port
        self.jenkins_user = user
        self.jenkins_pass = pswd
        self.conn = None
        return

    def connect(self):
        try:
            self.conn = jenkins.Jenkins('http://{0}:{1}'.format(self.jenkins_host, self.jenkins_port), username = self.jenkins_user, password = self.jenkins_pass)
        except Exception as e:
            print 'connect jenkins [http://{0}:{1}] Exception: {2}'.format(self.jenkins_host, self.jenkins_port, e)
        return

    def is_job_exist(self, job_name):
        is_exist = None
        try:
            if self.conn.get_job_name(job_name):
                is_exist = True
            else:
                is_exist = False
        except Exception as e:
            print 'get job [{0}] Exception: {1}'.format(job_name, e)
        return is_exist

    def create_job(self, job_name, xml_file):
        with open(xml_file) as file_handler:
            config_xml = file_handler.read()

        if not self.is_job_exist(job_name):
            self.conn.create_job(job_name, config_xml)
        else:
           self.conn.reconfig_job(job_name, config_xml)
        return

    def delete_job(self, job_name):
        if self.is_job_exist(job_name):
            self.conn.delete_job(job_name)
        return
