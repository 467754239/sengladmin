#!/usr/bin/python
#-*-coding:utf-8-*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
# copyright 2016 Wshuai, Inc.
# All Rights Reserved.

# @author: WShuai, Wshuai, Inc.

class CommResponse(object):
    def __init__(self):
        self.rsp_info = {
            # system
            200: '成功',
            29001: '参数错误',
            29002: '授权失败',
            # user
            21001: '该邮箱已经注册',
            21002: '注册验证码不正确',
            21003: '账号不存在',
            21004: '账号密码不匹配',
            21005: '原密码不正确',
            # datacenter,service,group
            22001: '该名称已存在',
            22002: '该名称不存在',
            22003: '状态已设置, 不需要重复设置',
            22004: '应用服务没有对应版本包',
            22005: '该数据中心下有未删除的部署组, 不允许删除',
            22006: '该健康检查已关联到部署组, 不允许删除',
            22007: '该监控已关联到部署组, 不允许删除',
            22008: '该数据中心不存在',
            22009: '该部署组不存在',
            22010: '该服务不存在',
            # config
            23001: '该配置已存在',
            23002: '该配置不存在',
            # package
            24001: '该版本已存在',
            24002: '该版本不存在',
            24003: '该版本正在升级, 不允许删除',
            24004: '该版本已经有审核拒绝状态, 该版本已失效',
            # deploy
            25001: '该版本未在开发环境部署, 不允许在该环境部署',
        }

    def generate_rsp_msg(self, rsp_code, rsp_data):
        try:
            rsp_info = self.rsp_info[rsp_code]
        except:
            rsp_info = 'failed'
        rsp_head = {
            'rsp_head': {
                'rsp_code': rsp_code,
                'rsp_info': rsp_info,
            }
        }
        if not rsp_data:
            return rsp_head
        else:
            return dict(rsp_head.items() + rsp_data.items())
