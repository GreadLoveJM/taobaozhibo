__author__ = 'pl'
# -*- coding:utf-8 -*-
import sys
import MySQLdb
import ConfigParser

reload(sys)
sys.setdefaultencoding('utf-8')


class Content(object):
    def __init__(self):
        self.host = "127.0.0.1"
        self.user = "root"
        self.passwd = "123456"
        self.port = 3306
        self.db = "abd"
        self.charset = "utf8"
        self.use_unicode = "True"
        self.conn = None
        self.cur = None
        self.initDb()

    def initDb(self):
        try:
            self.conn = MySQLdb.connect(host=self.host, port=self.port, user=self.user,
                                        passwd=self.passwd, db=self.db, charset=self.charset,
                                        use_unicode=self.use_unicode)
            self.cursor = self.conn.cursor()

        except MySQLdb.Error, e:
            print 'Mysql Error %d: %s' % (e.args[0], e.args[1])
            print 'Failed to connect to zhihu! Please check your config file and confirm your zhihu is open'
            sys.exit(-1)
        print 'Success connect zhihu'

    def insertIntoDB(self, m):

        self.cursor.execute('replace  into taobaolive VALUES (%s,%s,%s,%s,%s)', m)
        self.conn.commit()

    def closeResource(self):
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()


def main():
    pass


if __name__ == '__main__':
    main()
