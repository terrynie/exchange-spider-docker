#coding: utf-8
__author__ = 'terry'
import time
from exchange import exchange

#数据库连接信息
host=""        // MySQL host
user=""        // MySQL username
passwd=""      // MySQL password
dbname=""      // database name 
charset="utf8" // charset

ex = exchange()
conn = ex.makeConnectionToMySQL(host,user,passwd,dbname,charset)
while 1:
    contents = ex.readHtml()
    ex.splitAndStore(contents,conn)
    #每小时更新一次数据
    time.sleep(60)
