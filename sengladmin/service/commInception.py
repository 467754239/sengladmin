#!/usr/bin/python
# vim: tabstop=4 shiftwidth=4 softtabstop=4
#-*-coding:utf-8-*-
# copyright 2015 Sengled, Inc.
# All Rights Reserved.

# @author: WShuai, Sengled, Inc.

import MySQLdb

class InceptionHandler(object):
    def __init__(self, inception_host, inception_port, LOG = None):
        self.inception_host = inception_host
        self.inception_port = inception_port
        self.LOG = LOG
        return

    def audit(self, sql_str, addr, port, user, passwd, database):
        sql1 = '/*--user=%s;--password=%s;--host=%s;--check=1;--port=%s;*/ inception_magic_start; use %s;' % (
            user, passwd, host, port, database
        )
        sql2 = 'inception_magic_commit;'
        sql = sql1 + sql_str + sql2
        result = []
        try:
            conn = MySQLdb.connect(
                host = self.inception_host,
                port = self.inception_port,
                user = 'root',
                passwd = '',
                db = '',
                use_unicode = True,
                charset = 'utf8'
            )
            cur = conn.cursor()
            cur.execute(sql)
            ret = cur.fetchall()
            num_fields = len(cur.description)
            field_names = [i[0] for i in cur.description]
            for row in ret:
                if row[0] == 1:
                    continue
                if row[4] != 'None':
                    result.append((row[5],row[3],row[4]))
            cur.close()
            conn.close()
        except MySQLdb.Error, e:
            self.LOG.error('Mysql Error {0}: {1}'.format(e.args[0], e.args[1]))
            result.append('Exception')

        if not result:
            return True
        else:
            return False
