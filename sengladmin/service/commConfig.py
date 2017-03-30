#!/usr/bin/python
# -*- coding:utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
# copyright 2016 Wshuai, Inc.
# All Rights Reserved.

# @author: WShuai Inc.

import ConfigParser

class ConfigHandler(ConfigParser.ConfigParser):
    def __init__(self,defaults = None):
        ConfigParser.ConfigParser.__init__(self, defaults = None)  
        return
    def optionxform(self, optionstr):  
        return optionstr
