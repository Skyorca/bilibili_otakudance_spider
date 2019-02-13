import mysql.connector
from mysql.connector import errorcode
from mysql.connector import pooling
import time
import global_var

class MySQLManager:
    dbconfig = {
        "database": "bilibili_otakudance",
        "host"    : "localhost",
        "user"    : "root",
        "password": ""
    } 
    manage_tables = {}
    manage_tables["video"] = (
        "CREATE TABLE video ("
        "`aid`   int(11) NOT NULL,"
        "`cid`   int(11) NOT NULL,"
        "`mid`   int(11) NOT NULL,"
        "`video_name` varchar(512) NOT NULL,"
        "`up_name`    varchar(64)  NOT NULL,"
        "`view`   int(11) NOT NULL,"
        "`danmaku` int(11) NOT NULL,"
        "`reply` int(11) NOT NULL,"
        "`favorite` int(11) NOT NULL,"
        "`coin` int(11) NOT NULL,"
        "`share` int(11) NOT NULL,"
        "`like` int(11) NOT NULL,"
        "`history_rank` int(11) NOT NULL,"
        "PRIMARY KEY (`aid`),"
        "UNIQUE (`aid`)"        
        ") ENGINE=InnoDB"
    )
    manage_tables["up"] = (
        "CREATE TABLE up ("
        "`mid` int(11) NOT NULL,"
        "`up_name` varchar(64) NOT NULL,"
        "`sex`     varchar(16) NOT NULL DEFAULT 'UNKNOWN',"
        "`avatar`  varchar(256) NOT NULL DEFAULT '',"
        "`sign`    varchar(512) NOT NULL DEFAULT '',"
        "UNIQUE(`mid`),"
        "PRIMARY KEY(`mid`)"
        ") ENGINE = InnoDB"
    )
    manage_tables["danmaku"] = (
        "CREATE TABLE danmaku ("
        "`aid` int(11) NOT NULL,"
        "`cid` int(11) NOT NULL,"
        "`content` varchar(10240) NOT NULL DEFAULT '',"
        "`pubtime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,"
        "UNIQUE(`aid`),"
        "PRIMARY KEY (`aid`)"
        ") ENGINE= InnoDB"
    )

    def __init__(self, pool_size = 3):
        '''
        初始化数据库：不存在则建立，存在则建立tables
        '''
        try:
            con = mysql.connector.connect(user = self.dbconfig["user"], password = self.dbconfig["password"])
        except mysql.connector.Error as err:    #要是连接server出错就没有办法了
            print(err)         
            return
        cur = con.cursor()
        try:
            con.database = self.dbconfig["database"]
        except mysql.connector.Error as err:    #连接特定的数据库出错，很可能是数据库不存在，启动except里面的纠错机制
            if err.errno == errorcode.ER_BAD_DB_ERROR:
                self.create_database(cur)       #建立特定数据库
                con.database = self.dbconfig["database"]
                
        finally: 
            self.create_tables(cur)  
           #self.create_danmaku(cur)
            cur.close()
            con.close()
        #建立数据库基本信息是单次连接，随后释放掉了，接下来我们要建立一个内部的连接池供其他函数使用
        self.con_pool = pooling.MySQLConnectionPool(pool_name = "smth_pool", **self.dbconfig)


    def create_database(self, cursor):
        '''
        '''
        try:
            cursor.execute(
                "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(self.dbconfig["database"])
            )
            print("DATABSE {} ESTABLISHED ! ! !".format(self.dbconfig["database"]))
        except mysql.connector.Error as err:
            print(err)
            exit(1)
        
    def create_tables(self, cursor):
        '''
        依照manage_tables中对各个所需表单的建立语句对各表单进行建立
        '''
        try:
            for table_name, op in self.manage_tables.items():
                cursor.execute(op)
                print("TABLE {} ESTABLISHED ! ! !".format(table_name))
            print("ALL TABLES ESTABLISHED ! ! !")
        except  mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR: print(err)
            else: print(err)


    def insert_video(self, video_core_info):
        try:
            con = self.con_pool.get_connection()
            cur = con.cursor()
            sql = ("INSERT INTO video (`aid`,`cid`,`mid`,`video_name`,"
                   "`up_name`,`view`,`danmaku`,`reply`, `favorite`,`coin`,`share`,`like`,"
                   "`history_rank`,`pubtime`) VALUES ('{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}',from_unixtime('{}'))").format(
                    video_core_info['aid'], video_core_info['cid'], video_core_info['mid'],video_core_info['video_name'],
                    video_core_info['up_name'],video_core_info['view'], video_core_info['danmaku'],video_core_info['reply'],
                    video_core_info['favorite'],video_core_info['coin'],video_core_info['share'],video_core_info['like'],
                    video_core_info['history_rank'],video_core_info['pubtime']
                   )   #这个时间戳的写入方式非常重要！！！
           # print(sql)
            cur.execute(sql)
            con.commit()
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_DUP_UNIQUE or errorcode.ER_DUP_ENTRY: pass
            else:
                print("VIDEO-ERR: ", err)
                exit(1)
        finally:
            cur.close()
            con.close()


    def insert_up(self, up_core_info):
        '''
        '''
        try:
            con = self.con_pool.get_connection()
            cur = con.cursor()
            sql = ("INSERT INTO up (`mid`,`up_name`,`sex`,`avatar`,"
                   "`sign`) VALUES('{}','{}','{}','{}','{}')").format(
                    up_core_info['mid'], up_core_info['up_name'], up_core_info['sex'], 
                    up_core_info['avatar'], up_core_info['sign']
                   )
           # print(sql)
            cur.execute(sql)
            con.commit()
        except mysql.connector.Error as err:
            #因为可能会反复爬到同一个up的信息，这时不能停下来，只要过滤掉这些错误就好了。但是唯一值一定要指定。
            if err.errno == errorcode.ER_DUP_UNIQUE or errorcode.ER_DUP_ENTRY: pass
            else:
                print("UP-ERR: ", err)
                exit(1)
        finally:
            cur.close()
            con.close()
    

    def insert_danmaku(self, danmaku_core_info):
        '''
        '''
        try:
            con = self.con_pool.get_connection()
            cur = con.cursor()
            sql = ("INSERT INTO danmaku (`aid`,`cid`,`content`,`pubtime`"
                   ") VALUES('{}','{}','{}',from_unixtime('{}'))").format(
                    danmaku_core_info['aid'], danmaku_core_info['cid'],
                    danmaku_core_info['content'], danmaku_core_info['pubtime']
                   )
           # print(sql)
            cur.execute(sql)
            con.commit()
        except mysql.connector.Error as err:
            #因为可能会反复爬到同一个up的信息，这时不能停下来，只要过滤掉这些错误就好了。但是唯一值一定要指定。
            if err.errno == errorcode.ER_DUP_UNIQUE or errorcode.ER_DUP_ENTRY: pass
            else:
                print("DANMAKU-ERR: ", err)
                exit(1)
        finally:
            cur.close()
            con.close()




    def dump_csv(self):
        '''
        '''
        try:
            con = self.con_pool.get_connection()
            cur = con.cursor()
            dump_up = ("SELECT * INTO OUTFILE '/Users/apple/Desktop/up.csv' FIELDS TERMINATED BY ',' ENCLOSED BY '\"' LINES TERMINATED BY '\r\n' FROM (SELECT 'mid','up_name','sex','avatar','sign' UNION SELECT mid, up_name, sex, avatar, sign from up) b")
            cur.execute(dump_up)
            print("DUMP UP COMPLETED!")
            ###以下这句话总提示在UNION SELECT前面有语法错误，所以只好手动加标题###
            #dump_video = ("SELECT * INTO OUTFILE '/Users/apple/Desktop/video.csv' FIELDS TERMINATED BY ',' ENCLOSED BY '\"' LINES TERMINATED BY '\r\n' FROM (SELECT 'aid','cid','mid','video_name','up_name','view','danmaku','reply','favorite','coin','share','like','history_rank','pubtime' UNION SELECT aid, cid, mid, video_name, up_name, view, danmaku, reply, favorite, coin, share, like, history_rank, pubtime from video) b")
            dump_video = ("SELECT * FROM video INTO OUTFILE '/Users/apple/Desktop/video.csv' FIELDS TERMINATED BY ',' ENCLOSED BY '\"' LINES TERMINATED BY '\r\n' ")
            cur.execute(dump_video)
            print("DUMP VIDEO COMPLETED!")
            dump_danmaku = ("SELECT * INTO OUTFILE '/Users/apple/Desktop/danmaku.csv' FIELDS TERMINATED BY ',' ENCLOSED BY '\"' LINES TERMINATED BY '\r\n' FROM (SELECT 'aid','cid','content','pubtime' UNION SELECT aid,cid,content,pubtime from danmaku) b")
            cur.execute(dump_danmaku)
            print("DUMP DANMAKU COMPLETED!")
        except mysql.connector.Error as err:
            print("DUMP-ERR:", err)
            exit(1)
        finally:
            cur.close()
            con.close()



 #辅助函数1
    def insert_video_time(self):
        '''
        一开始没在table表里加时间，现在新增一列表示时间，这个函数只要调用一次就够了
        '''
        try:
            con = self.con_pool.get_connection()
            cur = con.cursor()
            sql = ("ALTER TABLE video ADD pubtime timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP AFTER history_rank")
            cur.execute(sql)
            con.commit()
        except mysql.connector.Error as err:
                print(err)
                exit(1)
        finally:
            cur.close()
            con.close()

    #辅助函数2
    def get_time_content(self):
        '''
        给之前的行增添新列内容pubtime，7k多个
        '''
        try:
            con = self.con_pool.get_connection()
            cur = con.cursor()
            sql = ("SELECT aid FROM video")
            cur.execute(sql)
            rows = cur.fetchall()
        except mysql.connector.Error as err:
                print(err)
                exit(1)
        finally:
            cur.close()
            con.close()
        return rows

    #辅助函数3
    def insert_time_content(self, aid, pubtime):
        '''
        '''
        try:
            con = self.con_pool.get_connection()
            cur = con.cursor()
            sql = ("UPDATE video SET pubtime=from_unixtime({}) WHERE aid={}".format(pubtime,aid))
            cur.execute(sql)
            con.commit()
        except mysql.connector.Error as err:
                print(err)
                exit(1)
        finally:
            cur.close()
            con.close()

    #辅助函数4：新增danmaku表
    def create_danmaku(self, cur):
        try:
            cur.execute(self.manage_tables["danmaku"])
            print("DANMAKU TABLE READY !!!")
        except mysql.connector.Error as err:
            print(err)

        

if __name__ == "__main__":
    mgr = MySQLManager(1)

# /usr/local/var/mysql 是mysql存放数据的路径
# /usr/local/Cellar/mysql/8.0.12/.bottle/etc/my.cnf 配置文件路径 这个修改后放到/private/etc下面才生效（restart mysql.server）




