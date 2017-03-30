#!/usr/bin/python
#-*-coding:utf-8-*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
# copyright 2016 Wshuai, Inc.
# All Rights Reserved.

# @author: WShuai, Wshuai, Inc.

import os
import json
import uuid
import consul

class CommConsul(object):
    def __init__(self, crt_str, key_str, LOG = None):
        self.crt_str = crt_str
        self.key_str = key_str
        self.LOG = LOG
        uuid_str = str(uuid.uuid4())
        self.crt_file = os.path.join('/tmp', 'consul_%s.cer' % uuid_str)
        self.key_file = os.path.join('/tmp', 'consul_%s.key' % uuid_str)
        self.timeout = 5 
        self.consul_conn = None
        self.cert = None
        self.host = None
        self.port = None
        return

    def save_consul_cert(self):
        crt_file_handler = open(self.crt_file, 'w')
        crt_file_handler.write(self.crt_str.replace('\\n', '\n'))
        crt_file_handler.close()
        key_file_handler = open(self.key_file, 'w')
        key_file_handler.write(self.key_str.replace('\\n', '\n'))
        key_file_handler.close()
        self.cert = (self.crt_file, self.key_file)
        return

    def clear_consul_cert(self):
        try:
            os.remove(self.crt_file)
            os.remove(self.key_file)
        finally:
            return
        
    def connect(self, host, port):
        self.host = host
        self.port = port
        self.save_consul_cert()
        self.consul_conn = consul.Consul(host = host, port = self.port, verify = False, scheme = 'https', cert = self.cert)
        if not self.consul_conn:
            return False
        return True

    def get_values(self, key):
        try:
            rsp_info = self.consul_conn.kv.get(key, timeout = self.timeout)
            try:
                return json.loads(rsp_info[1]['Value'])
            except:
                return rsp_info[1]['Value']
        except Exception as e:
            self.LOG.error('get {0} value from consul {1} failed: {2}'.format(key, self.host, e))
            return None

    def put_values(self, key, value):
        try:
            ret = self.consul_conn.kv.put(key, value, timeout = self.timeout)
            self.LOG.debug('put {0} value to consul {1} success'.format(key, self.host))
            return ret
        except Exception as e:
            self.LOG.error('put {0} value to consul {1} failed: {2}'.format(key, self.host, e))
            return False

    def del_values(self, key):
        try:
            ret = self.consul_conn.kv.delete(key, recurse = True, timeout = self.timeout)
            self.LOG.debug('delete {0} value from consul {1} success'.format(key, self.host))
            return ret
        except Exception as e:
            self.LOG.error('delete {0} value from consul {1} failed: {2}'.format(key, self.host, e))
            return False

    def get_consul_instances(self, service_name):
        health_list = []
        try:
            results = self.consul_conn.health.service(service_name)[1]
            if results:
                for result in results:
                    health = True
                    for check in result['Checks']:
                        if check['Status'] == 'passing':
                            continue
                        else:
                            health = False
                            break
                    if health:
                        health_list.append(result['Node'].get('Address'))
            else:
                self.LOG.debug('consul {0} has not {1} service info'.format(self.host, service_name))
        except Exception as e:
            self.LOG.error('get {0} health from consul {1} failed: {2}'.format(service_name, self.host, e))
        return health_list
