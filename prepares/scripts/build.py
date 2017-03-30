#!/usr/bin/python
#-*-coding:utf-8-*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
# copyright 2015 Sengled, Inc.
# All Rights Reserved.

# @author: WShuai, Sengled, Inc.


import yaml

class YamlHandler(object):
    def __init__(self, file):
        self.file = file
        self.yaml_content = None
        return

    def load(self):
        try:
            with open(self.file) as file_handler:
                self.yaml_content = yaml.load(file_handler)
            return True
        except Exception as e:
            print('open yaml file {0} failed: {1}'.format(self.file, e))
            return False

    def process_phases(self, steps):
        step_commands = []
        for step in steps:
            if self.yaml_content['phases'][step]['commands']:
                step_commands += self.yaml_content['phases'][step]['commands']
        return step_commands

    def process_artifacts(self):
        return self.yaml_content['artifacts']['files'] if self.yaml_content['artifacts']['files'] else []

    def process_targets(self):
        targets = []
        try:
            targets = self.yaml_content['targets']['files'] if self.yaml_content['targets']['files'] else []
        except:
            targets = []
        return targets

        
########################################################
import boto3
class S3Handler(object):
    def __init__(self, region_name, access_key_id, secret_access_key):
        self.region_name = region_name
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key
        self.bucket_name = None
        self.bucket = None
        self.conn = None
        self.region = None
        return

    def connect(self):
        if self.conn:
            return
        try:
            self.conn = boto3.resource(
                's3',
                region_name = self.region_name,
                aws_access_key_id = self.access_key_id,
                aws_secret_access_key = self.secret_access_key
            )
        except Exception as e:
            print('connect to aws s3 failed, {0}'.format(e))
        return
    
    def put_file(self, bucket_name, remote_path_file, local_path_file):
        self.bucket = self.conn.Bucket(bucket_name)
        self.bucket.upload_file(local_path_file, remote_path_file)
        return

########################################################    
import requests

class HttpClient(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        return

    def put(self, url, json_body):
        request_url = 'http://{0}:{1}/{2}'.format(self.host, self.port, url)
        try:
            result = requests.put(request_url, data = json_body, timeout = 15)
            print result.status_code
            if result.status_code != 200:
                data = False
            else:
                data = result.text
        except Exception as e:
            print('requests put [{0}] failed: {1}'.format(request_url, e))
            data = False
        return data
########################################################
import os
import sys
import hashlib
import commands
CONFIG_ENV = {
    'service': None,
    'version': None,
    'git_url': None,
    's3_region': None,
    's3_access_key_id': None,
    's3_secret_access_key': None,
    's3_bucket': None,
    's3_url': None,
    'platform_host': None,
    'platform_port': None,
    'platform_url': None
}
CONFIG_DEFAULT = {
    'git_local_path': '/tmp/build/gitrepo',
    'tar_list': [
        'appspec.yml',
        'config',
        'content',
        'endpoint',
        'execenv',
        'release_note',
        'scripts',
        'sql'
    ]
}
BUILD_STEPS = [
    'install', 'pre_build', 'build', 'post_build'
]
def main():
    # get environment
    for key in CONFIG_ENV.keys():
        CONFIG_ENV[key] = os.environ.get(key)
        if not CONFIG_ENV[key]:
            print('get environment variables failed: {0}'.format(key))
            return False
    print('get environment variables success: {0}'.format(CONFIG_ENV))
    
    # get code
    if not os.path.exists(CONFIG_DEFAULT['git_local_path']):
        os.makedirs(CONFIG_DEFAULT['git_local_path'])
    status, output = commands.getstatusoutput(
        'cd {0}; git clone {1}; cd {2}; git checkout -b build {3}; cd -'.format(
            CONFIG_DEFAULT['git_local_path'],
            CONFIG_ENV['git_url'],
            CONFIG_ENV['service'],
            CONFIG_ENV['version']
        )
    )
    print('status is [{0}], output is [{1}]'.format(status, output))
    
    
    # get build command, and artifacts, and targets
    yaml_handler = YamlHandler(os.path.join(CONFIG_DEFAULT['git_local_path'], CONFIG_ENV['service'], 'buildspec.yml'))
    if not yaml_handler.load():
        return False
    build_commands = yaml_handler.process_phases(BUILD_STEPS)
    target_artifacts = yaml_handler.process_artifacts()
    target_files = yaml_handler.process_targets()
    
    # exec command
    base_work_path = os.getcwd()
    os.chdir(os.path.join(CONFIG_DEFAULT['git_local_path'], CONFIG_ENV['service']))
    for build_command in build_commands:
        print('exec command [{0}] begin'.format(build_command))
        status, output = commands.getstatusoutput(build_command)
        if 0 != status:
            print('exec command [{0}] failed: [{1}], [{2}]'.format(build_command, status, output))
            return
        print('exec command [{0}] success: [{1}], [{2}]'.format(build_command, status, output))
    os.chdir(base_work_path)
            
    # move target
    for target_artifact in target_artifacts:
        if not os.path.isfile(os.path.join(CONFIG_DEFAULT['git_local_path'], CONFIG_ENV['service'], target_artifact['source'])):
            print('target artifact [{0}] not found.'.format(target_artifact))
            return False
        if not os.path.exists(os.path.join(CONFIG_DEFAULT['git_local_path'], CONFIG_ENV['service'], target_artifact['destination'])):
            os.makedirs(os.path.join(CONFIG_DEFAULT['git_local_path'], CONFIG_ENV['service'], target_artifact['destination']))

        if target_artifact['action'] == 'unzip':
            cmd = '{0} -o {1} -d {2}'.format(
                target_artifact['action'],
                os.path.join(CONFIG_DEFAULT['git_local_path'], CONFIG_ENV['service'], target_artifact['source']),
                os.path.join(CONFIG_DEFAULT['git_local_path'], CONFIG_ENV['service'], target_artifact['destination'])
            )
        else:
            cmd = '{0} {1} {2}'.format(
                target_artifact['action'],
                os.path.join(CONFIG_DEFAULT['git_local_path'], CONFIG_ENV['service'], target_artifact['source']),
                os.path.join(CONFIG_DEFAULT['git_local_path'], CONFIG_ENV['service'], target_artifact['destination'])
            )
        print('exec command [{0}] begin'.format(cmd))
        status, output = commands.getstatusoutput(cmd)
        if 0 != status:
            print('exec command [{0}] failed: [{1}], [{2}]'.format(cmd, status, output))
            return False
        print('exec command [{0}] success: [{1}], [{2}]'.format(cmd, status, output))

    # update version in appspec.yml
    cmd = "sed -i 's/APP_VERSION/{0}/g' {1}".format(CONFIG_ENV['version'], os.path.join(CONFIG_DEFAULT['git_local_path'], CONFIG_ENV['service'], 'appspec.yml'))
    print('exec command [{0}] begin'.format(cmd))
    status, output = commands.getstatusoutput(cmd)
    print('exec command [{0}] success: [{1}], [{2}]'.format(cmd, status, output))

    # tar package
    os.chdir(os.path.join(CONFIG_DEFAULT['git_local_path'], CONFIG_ENV['service']))
    if CONFIG_ENV['service'] == 'agent':
        cmd = 'tar -zcvf {0}.tar.gz {1}'.format(CONFIG_ENV['service'], ' '.join(target_files))
    else:
        cmd = 'tar -zcvf {0}.tar.gz {1}'.format(CONFIG_ENV['service'], ' '.join(CONFIG_DEFAULT['tar_list']))
    print('exec command [{0}] begin'.format(cmd))
    status, output = commands.getstatusoutput(cmd)
    if 0 != status:
        print('exec command [{0}] failed: [{1}], [{2}]'.format(cmd, status, output))
        return False
    print('exec command [{0}] success: [{1}], [{2}]'.format(cmd, status, output))
    os.chdir(base_work_path)
    
    # md5
    with open(os.path.join(CONFIG_DEFAULT['git_local_path'], CONFIG_ENV['service'], '{0}.tar.gz'.format(CONFIG_ENV['service'])), 'rb') as file_handler:
        verify = hashlib.md5(file_handler.read()).hexdigest()
    print('version package md5 is [{0}]'.format(verify))
    
    # upload s3  put_file(self, bucket_name, remote_path_file, local_path_file):
    s3_handler = S3Handler(CONFIG_ENV['s3_region'], CONFIG_ENV['s3_access_key_id'], CONFIG_ENV['s3_secret_access_key'])
    s3_handler.connect()
    s3_handler.put_file(
        CONFIG_ENV['s3_bucket'], 
        CONFIG_ENV['s3_url'], 
        os.path.join(CONFIG_DEFAULT['git_local_path'], CONFIG_ENV['service'], '{0}.tar.gz'.format(CONFIG_ENV['service']))
    )
    
    # call platform api
    parameters = {
        'service': CONFIG_ENV['service'],
        'version': CONFIG_ENV['version'],
        'md5': verify,
        'region': CONFIG_ENV['s3_region'],
        'bucket': CONFIG_ENV['s3_bucket'],
        'file_path': CONFIG_ENV['s3_url']
    }
    http_client = HttpClient(CONFIG_ENV['platform_host'], int(CONFIG_ENV['platform_port']))
    result = http_client.put(CONFIG_ENV['platform_url'], parameters)
    print('call platform api success')
    return
    
if __name__ == '__main__':
    main()
    sys.exit(0)
