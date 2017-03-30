#!/usr/bin/python
#-*-coding:utf-8-*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
# copyright 2017 Wshuai, Inc.
# All Rights Reserved.

# @author: WShuai, Wshuai, Inc.

import os
import sys
import docker
import yaml
import shutil
  
class DefaultConfig(object):
    git_local_repo_path = '/tmp'
    s3_region = 'cn-north-1'
    s3_access_key_id = 'xxxxx'
    s3_secret_access_key = 'xxxxx'
    s3_bucket = 'xxxx'
    s3_bucket_name = 'xxxx'
    platform_host = 'platform.cloud.sengled.com'
    platform_port = '8090'
    platform_url = 'sengladmin/package/'
    docker_url = 'tcp://219.232.105.116:2375'
    docker_java = '/data/java'
    docker_maven = '/data/apache-maven-3.3.9'
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

    def process_exenv(self):
        exec_envs = []
        try:
            exec_envs = self.yaml_content['exec'] if self.yaml_content['exec'] else []
        except Exception as e:
            print('get exec failed: {0}'.format('exec'))
        return exec_envs

class Package(object):
    def __init__(self, service, git_path):
        self.service = service
        self.git_path = git_path
        self.git_version = '{0}:sengled/service-version'.format(git_path.split(':')[0])
        self.local_repo_path_service = os.path.join(DefaultConfig.git_local_repo_path, service)
        self.local_repo_path_version = os.path.join(DefaultConfig.git_local_repo_path, 'service-version')
        self.local_repo_file_version = os.path.join(DefaultConfig.git_local_repo_path, 'service-version', '{0}.version'.format(service))
        return

    def get_new_version(self):
        last_version = None
        new_version = None
        if not os.path.exists(self.local_repo_path_version):
            cmd = 'git clone {0} {1}'.format(self.git_version, self.local_repo_path_version)
        else:
            cmd = 'cd {0}; git pull; cd -'.format(self.local_repo_path_version)

        print('exec command [{0}]'.format(cmd))
        os.system(cmd)

        if os.path.isfile(self.local_repo_file_version):
            with open(self.local_repo_file_version) as file_handler:
                last_version = file_handler.read()
        if not last_version:
            new_version = 'v1.0.0'
        else:
            major_version = int(last_version[1:].split('.')[0])
            minor_version = int(last_version[1:].split('.')[1])
            revise_version = int(last_version[1:].split('.')[2])
            if revise_version < 99:
                revise_version += 1
            else:
                revise_version = 0
                minor_version += 1

            if minor_version == 10:
                minor_version = 0
                major_version += 1
            new_version = 'v{0}.{1}.{2}'.format(major_version, minor_version, revise_version)

        with open(self.local_repo_file_version, 'w') as file_handler:
            file_handler.write(new_version)
        os.system('cd {0}; git add .; git commit -m "update version"; git push; cd -'.format(self.local_repo_path_version))
        return new_version

    def tag_git(self, new_version):
        if not os.path.exists(self.local_repo_path_service):
            os.system('git clone {0} {1}'.format(self.git_path, self.local_repo_path_service))
        else:
            os.system('cd {0}; git pull; cd -'.format(self.local_repo_path_service))

        os.system('cd {0}; git tag -af {1} -m {1}; git push origin --delete tag {1}; git push origin {1}; cd -'.format(self.local_repo_path_service, new_version))       
        return

    def get_java_version(self):
        java_version = '1.8'
        yaml_handler = YamlHandler(os.path.join(self.local_repo_path_service, 'execenv', 'execenv.yml'))
        if yaml_handler.load():
            try:
                exec_envs = yaml_handler.process_exenv()
                for exec_env in exec_envs:
                    if exec_env['type'] == 'java':
                        java_version = exec_env['version']
            except Exception as e:
                print 'get java version failed: {0}'.format(e)
        return java_version
        
    def get_package_info(self):
        new_version = self.get_new_version()
        self.tag_git(new_version)
        s3_url = 'applications/{0}/{1}/{0}.tar.gz'.format(self.service, new_version)
        return (self.service, new_version, self.git_path, DefaultConfig.s3_bucket, s3_url)

    def clear(self):
        shutil.rmtree(self.local_repo_path_service)
        return

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('build-package.py args error. USAGE: python build-package.py {service_name} {service_git_path} {build_docker_image_id}')
        sys.exit(1)

    package = Package(sys.argv[1], sys.argv[2])
    package_info = package.get_package_info()
    java_version = package.get_java_version()

    image = sys.argv[3]
    volumes = {
        '{0}{1}'.format(DefaultConfig.docker_java, java_version) :{
            'bind': '/usr/local/java'
        },
        DefaultConfig.docker_maven :{
            'bind': '/usr/local/maven'
        },
        '/data/build': {
            'bind': '/mnt'
        }
    }
    environment = {
        'service': package_info[0],
        'version': package_info[1],
        'git_url': package_info[2],
        's3_region': DefaultConfig.s3_region,
        's3_access_key_id': DefaultConfig.s3_access_key_id,
        's3_secret_access_key': DefaultConfig.s3_secret_access_key,
        's3_bucket': package_info[3],
        's3_url': package_info[4],
        'platform_host': DefaultConfig.platform_host,
        'platform_port': DefaultConfig.platform_port,
        'platform_url': DefaultConfig.platform_url
    }
    cmd = "sh -c 'source /etc/profile && python /mnt/build.py'"
    print('image is [{0}]'.format(image))
    print('volumes is [{0}]'.format(volumes))
    print('environment is [{0}]'.format(environment))
    print('cmd is [{0}]'.format(cmd))
    docker_client = docker.DockerClient(base_url= DefaultConfig.docker_url)
    print docker_client.containers.run(
        image,
        stdout = True,
        volumes = volumes,
        environment = environment,
        command = cmd
    )
    print('current service version is [{0}]'.format(package_info[1]))
    print('===========finish==========')
    sys.exit(0)
