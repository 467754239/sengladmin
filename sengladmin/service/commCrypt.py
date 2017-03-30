#!/usr/bin/python
# -*- coding:utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
# copyright 2016 WShuai, Inc.
# All Rights Reserved.

# @author: WShuai, WShuai, Inc.

import base64
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex

class CryptHandler(object):
    def __init__(self):
        self.key = "asdfghjkl;'wudan"
        self.mode = AES.MODE_CBC

    def encrypt(self, text):
        cryptor = AES.new(self.key, self.mode, self.key)
        length = 16
        count = len(text)
        add = length - (count % length)
        text = text + ('\0' * add)
        self.ciphertext = cryptor.encrypt(text)
        return base64.b64encode(b2a_hex(self.ciphertext))

    def decrypt(self, text):
        try:
            cryptor = AES.new(self.key, self.mode, self.key)
            plain_text = cryptor.decrypt(a2b_hex(base64.b64decode(text)))
            return plain_text.rstrip('\0')
        except:
            return '213'
