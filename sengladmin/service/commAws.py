#!/usr/bin/python
#-*-coding:utf-8-*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
# copyright 2016 Wshuai, Inc.
# All Rights Reserved.

# @author: WShuai, Wshuai, Inc.

import boto3

class S3Handler(object):
    def __init__(self, region_name, access_key_id, secret_access_key, LOG = None):
        self.region_name = region_name
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key
        self.bucket_name = None
        self.bucket = None
        self.conn = None
        self.region = None
        self.LOG = LOG
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
            self.LOG.error('connect to aws s3 failed, {0}'.format(e))
        return

    def get_file(self, bucket_name, remote_path_file, local_path_file):
        self.bucket = self.conn.Bucket(bucket_name)
        self.bucket.download_file(remote_path_file, local_path_file)
        return

    def put_file(self, bucket_name, remote_path_file, local_path_file):
        self.bucket = self.conn.Bucket(bucket_name)
        self.bucket.upload_file(local_path_file, remote_path_file)
        return
