from __future__ import unicode_literals

from django.conf import settings
from django.db import models
from mongoengine import *

# Create your models here.

connect(
    host = 'mongodb://%s:%s@%s:%s/%s' % ( 
        settings.MONGODB['default']['USER'],
        settings.MONGODB['default']['PASSWORD'],
        settings.MONGODB['default']['HOST'],
        settings.MONGODB['default']['PORT'],
        settings.MONGODB['default']['NAME']
    )
)

class User(Document):
    account = StringField(required = True)
    password = StringField(required = True)
    username = StringField(required = True)
    phone = StringField(required = True)
    create_time = StringField(required = True)
    last_time = StringField(required = False)
    role = StringField(required = False)

class Role(Document):
    name = StringField(required = True)
    level = IntField(required = True)
    description = StringField(required = True)
    permissions = ListField(required = False)
    users = ListField(required = False)

class Permission(Document):
    name = StringField(required = True)
    description = StringField(required = True)
    url = StringField(required = True)
    superior = StringField(required = True)
    roles = ListField(required = False)
    index = StringField(required = False)

class Syslog(Document):
    time = StringField(required = True)
    operation = StringField(required = True)
    user = StringField(required = True)
    addr = StringField(required = True)

class Datacenter(Document):
    name = StringField(required = True)
    location = StringField(required = True)
    env = StringField(required = True)
    type = StringField(required = True)
    region = StringField(required = True)
    status = StringField(required = True)
    agent = DictField(required = True)
    deploy = DictField(required = True)
    qurom = DictField(required = True)

class Service(Document):
    name = StringField(required = True)
    description = StringField(required = True)
    git_path = StringField(required = True)
    #build_env = DictField(required = False)
    build_trigger = StringField(required = True)
    build_docker_image = StringField(required = True)
    datacenters = ListField(required = False)
    status = StringField(required = True)
    endpoints = ListField(required = False)

class DeployGroup(Document):
    name = StringField(required = True)
    datacenter = StringField(required = True)
    service = StringField(required = True)
    version = StringField(required = True)
    group = DictField(required = True)
    deploy = DictField(required = True)
    healthchecks = ListField(required = False)
    monitors = ListField(required = False)
  
class Config(Document):
    key = StringField(required = True)
    value = StringField(required = True)
    consul_key = StringField(required = True)
    consul_value = StringField(required = True)
    datacenter = StringField(required = True)
    domain = StringField(required = True)
    description = StringField(required = False)

class Package(Document):
    service = StringField(required = True)
    version = StringField(required = True)
    md5 = DictField(required = True)
    file_path = StringField(required = True)
    region = StringField(required = True)
    bucket = StringField(required = True)
    time = StringField(required = True)
    testing = StringField(required = False)
    status = DictField(required = False)
    audit = DictField(required = False)
    
class Health(Document):
    name = StringField(required = True)
    type = StringField(required = True)
    value = StringField(required = True)
    interval = IntField(required = True)
    timeout = IntField(required = True)
    pending = IntField(required = True)
    healthy_threshold = IntField(required = True)
    unhealthy_threshold = IntField(required = True)
    failback = StringField(required = True)
    associate = BooleanField(required = True)
    groups = ListField(required = False)

class Monitor(Document):
    name = StringField(required = True)
    type = StringField(required = True)
    value = StringField(required = True)
    associate = BooleanField(required = True)
    groups = ListField(required = False)

class DeployRecord(Document):
    deploy_id = StringField(required = True)
    source_version = StringField(required = True)
    target_version = StringField(required = True)
    start_time = StringField(required = True)
    end_time = StringField(required = False)
    result = StringField(required = True)
    env = StringField(required = True)
    datacenter = StringField(required = True)
    group = StringField(required = True)
    service = StringField(required = True)
    operator = StringField(required = True)

class DeployProcess(Document):
    deploy_id = StringField(required = True)
    instance = StringField(required = True)
    result = StringField(required = True)
    start_time = StringField(required = True)
    end_time = StringField(required = False)

class DatacenterVersion(Document):
    datacenter = StringField(required = True)
    service = StringField(required = True)
    version = StringField(required = True)
    time = StringField(required = True)

class Consignee(Document):
    name = StringField(required = True)
    email = StringField(required = True)
    group = StringField(required = True)
    service = ListField(required = False)

class Event(Document):
    event_id = StringField(required = True)
    instance_id = StringField(required = True)
    group = StringField(required = True)
    description = StringField(required = True)
    additional = StringField(required = False)
    additional2 = StringField(required = False)
    additional3 = StringField(required = False)
    create_time = StringField(required = False)
