#!/usr/bin/python
# vim: tabstop=4 shiftwidth=4 softtabstop=4
#-*-coding:utf-8-*-
# copyright 2015 Sengled, Inc.
# All Rights Reserved.

# @author: WShuai, Sengled, Inc.

import uuid

class RandomHandler(object):
    def __init__(self):
        return
 
    def generate_code(self):
        code = str(uuid.uuid4()).replace('-','').upper()
        security_code = ''
        length = 0
        for char in code[::-1][:6]:
            try:
                security_code += str(int(char))
                length += 1
            except:
                security_code += str(ord(char))
                length += 2
            if length >= 6:
                break
        return security_code if len(security_code) == 6 else security_code[:6]
