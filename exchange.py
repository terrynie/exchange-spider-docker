#coding:utf-8
import urllib2
import cookielib
import re
import MySQLdb
import time

class exchange:

    # 将string转换为float
    def strToFloat(self,str):
        mFloat = 0.0
        if(str != ''):
            mFloat = float(str)
        return mFloat

    # 汇率表中插入新纪录
    def saveData(self,content,conn):
        cursor = conn.cursor()
        if(content[1] != ''):
            bank = content[0]
            currency = content[1]
            code = content[2]
            currencyUnit = content[3]
            cenPrice = self.strToFloat(content[4])
            remittanceBuyPrice = self.strToFloat(content[5])
            sellPrice = self.strToFloat(content[6])
            cashBuyPrice = self.strToFloat(content[7])
            sellPrice2 = self.strToFloat(content[8])
            releasedate = content[9]
            releasetime = content[10]
            timestamp = int(time.mktime(time.strptime((releasedate + ' ' + releasetime), '%Y-%m-%d %H:%M:%S')))
            print timestamp
            sql = "INSERT INTO exchange(bank, currency, code, currencyUnit, cenPrice, remittanceBuyPrice, sellPrice, cashBuyPrice, sellPrice2, releasedate, releasetime, timestamp, flag) VALUES('%s','%s','%s','%s','%f','%f','%f','%f','%f','%s','%s','%s','%d') " % (bank,currency,code,currencyUnit,cenPrice,remittanceBuyPrice,sellPrice,cashBuyPrice,sellPrice2,releasedate,releasetime,timestamp,1)
            cursor.execute(sql)
            conn.commit()

    #查询指定银行指定货币汇率的更新时间
    def queryUpdateTime(self,bank,currency,conn):
        cursor = conn.cursor()
        sql = "SELECT * FROM updateTime WHERE bank='%s' AND currency='%s'" % (bank, currency)
        cursor.execute(sql)
        result = cursor.fetchall()
        # releasedate = ''
        # for row in result:
        #      releasedate = row[2]
        # return releasedate
        return result

    #首次插入更新时间表
    def insertToUpdateTime(self, bank, currency, date, time, conn):
        cursor = conn.cursor()
        sql = "INSERT INTO updateTime(bank, currency, lastreleasedate, lastreleasetime) VALUES ('%s','%s','%s','%s')" % (bank, currency, date, time)
        cursor.execute(sql)
        conn.commit()

    #更新指定银行指定货币汇率的更新时间
    def updateTime(self,bank,currency,date,time,conn):
        cursor = conn.cursor()
        sql2 = "UPDATE exchange SET flag='%d' WHERE bank='%s' AND currency='%s' AND flag='%d'" % (-1, bank, currency,0)
        cursor.execute(sql2)
        sql1 = "UPDATE exchange SET flag='%d' WHERE bank='%s' AND currency='%s' AND flag='%d'" % (0, bank, currency,1)
        cursor.execute(sql1)
        sql = "UPDATE updateTime SET lastreleasedate='%s' , lastreleasetime='%s' WHERE bank='%s' AND currency='%s'" % (date, time, bank, currency)
        cursor.execute(sql)
        conn.commit()

    #将获取的数组进行分条操作
    def splitAndStore(self,contents,conn):
        for content in contents:
            #查看是否是第一次执行程序
            try:
                record = self.queryUpdateTime(content[0],content[1],conn)
                if(len(record)==0):
                    self.insertToUpdateTime(content[0],content[1],content[9],content[10],conn)
                    self.saveData(content,conn)
                if(record[len(record)-1][2] != content[9] or record[len(record)-1][3] != content[10]):
                    self.updateTime(content[0],content[1],content[9],content[10],conn)
                    self.saveData(content,conn)
            except :
                continue

    #读取网页内容并使用正则表达式进行提取,并返回数据
    def readHtml(self):
        request = urllib2.Request('http://data.bank.hexun.com/other/cms/foreignexchangejson.ashx?callback=ShowDatalist',data=None,headers = {
            'Connection': 'Keep-Alive',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4',
            'Cookie':self.getCookie(),
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36'
        })

        response = urllib2.urlopen(request)
        html = response.read()
        html = html.decode('gb2312','ignore').encode('utf-8')
        condition = "{bank:'(.*?)',currency:'(.*?)',code:'(.*?)',currencyUnit:'(.*?)',cenPrice:'(.*?)',buyPrice1:'(.*?)',sellPrice1:'(.*?)',buyPrice2:'(.*?)',sellPrice2:'(.*?)',releasedate:'(.*?) (.*?)'}"
        contents = re.findall(condition,html,re.S)
        return contents

    # 根据传入数据建立连接
    def makeConnectionToMySQL(self,host,user,passwd,dbname,charset):
        conn = MySQLdb.connect(host=host, user=user ,passwd=passwd, db=dbname, charset=charset)
        return conn

    def getCookie(self):
        url = 'http://data.bank.hexun.com/other/cms/foreignexchangejson.ashx?callback=ShowDatalist'
        # url = 'https://www.baidu.com'
        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        opener.addheaders = [('User-Agent','Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36')]
        urllib2.install_opener(opener)
        res = urllib2.urlopen(url)

        for index, co in enumerate(cj):
            return co.name + '=' + co.value

