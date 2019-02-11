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
                   "`history_rank`) VALUES('{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}')").format(
                    video_core_info['aid'], video_core_info['cid'], video_core_info['mid'],video_core_info['video_name'],
                    video_core_info['up_name'],video_core_info['view'], video_core_info['danmaku'],video_core_info['reply'],
                    video_core_info['favorite'],video_core_info['coin'],video_core_info['share'],video_core_info['like'],
                    video_core_info['history_rank']
                   )
            print(sql)
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
            print(sql)
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
    

    def dump_csv(self):
        '''
        '''
        try:
            con = self.con_pool.get_connection()
            cur = con.cursor()
            dump_up = ("SELECT * INTO OUTFILE '/Users/apple/Desktop/up.csv' FIELDS TERMINATED BY ',' ENCLOSED BY '\"' LINES TERMINATED BY '\r\n' FROM (SELECT 'mid','up_name','sex','avatar','sign' UNION SELECT mid, up_name, sex, avatar, sign from up) b")
            cur.execute(dump_up)
            print("DUMP UP COMPLETED!")
            #dump_video = ("SELECT * INTO OUTFILE '/Users/apple/Desktop/video.csv' FIELDS TERMINATED BY ',' ENCLOSED BY '\"' LINES TERMINATED BY '\r\n' FROM (SELECT 'aid','cid','mid','video_name','up_name','view','danmaku','reply','favorite','coin','share','like','history_rank' UNION SELECT aid, cid, mid, video_name, up_name, view, danmaku, reply, favorite, coin, share, like, history_rank from video) b")
            dump_video = ("SELECT * FROM video INTO OUTFILE '/Users/apple/Desktop/video.csv' FIELDS TERMINATED BY ',' ENCLOSED BY '\"' LINES TERMINATED BY '\r\n' ")
            cur.execute(dump_video)
            print("DUMP VIDEO COMPLETED!")
        except mysql.connector.Error as err:
            print("DUMP-ERR:", err)
            exit(1)
        finally:
            cur.close()
            con.close()

if __name__ == "__main__":
    mgr = MySQLManager(1)

# /usr/local/var/mysql 是mysql存放数据的路径
# /usr/local/Cellar/mysql/8.0.12/.bottle/etc/my.cnf 配置文件路径 这个修改后放到/private/etc下面才生效（restart mysql.server）
