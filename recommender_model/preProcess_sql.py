import pymysql
import pymysql.cursors
import numpy as np

class MysqlConnect(object):
    # 初始化, 构造函数
    def __init__(self, host='localhost',port=3306,user='libo',passwd='123567',db='testdb'):
        '''

        :param host: IP
        :param user: 用户名
        :param passwd: 密码
        :param port: 端口号
        :param db: 数据库名
        '''
        self.db = pymysql.Connect(host=host, user=user,port = port, password=passwd,database=db,charset='utf8')
        self.cursor = self.db.cursor()

    # 析构化 ,析构函数
    def __del__(self):
        self.cursor.close()
        self.db.close()

    # 将要插入的数据写成元组传入
    def exec_data(self, sql, data=None):
        # 执行SQL语句
        self.cursor.execute(sql, data)
        # 提交到数据库执行
        self.db.commit()

    # sql拼接时使用repr()，将字符串原样输出
    def exec(self, sql):
        self.cursor.execute(sql)
        # 提交到数据库执行
        self.db.commit()

    def select(self, sql):
        self.cursor.execute(sql)
        # 获取所有记录列表,返回结果为二维数组
        results = self.cursor.fetchall()
        datas = []
        for row in results:
            datas.append(list(row))
        return datas


    def get_article_content(self,user_cnt):
        '''

        :param user_cnt: 需要去指定规模的参数
        :return:
        '''
        sql = '''select article_id,category_id,title,SUBSTRING_INDEX(text,' ',50),time_stamp from rs_article_info where article_id in(
                    select distinct article_id from rs_member_history where member_id <(
                        select user_id from member_detail order by user_id limit %s,1));
        '''%(user_cnt)
        full_article_info = self.select(sql)
        return full_article_info

    def get_member_read_record(self,user_cnt):
        his_query = '''select member_id,article_id,time_stamp,impression from rs_member_history where member_id <(
                select user_id from member_detail order by user_id limit %s,1);'''%(user_cnt)
        member_read_record = self.select(his_query)
        return member_read_record



class PreProcess_sql:


    @staticmethod
    def PreprocessArticles(user_cnt=7558):
        mysql = MysqlConnect()
        full_article_info = mysql.get_article_content(user_cnt)

        art_ids, art_cates, art_contents, art_timestamp=[],[],[],[]
        for article in full_article_info:
            art_ids.append(article[0])
            art_cates.append(article[1])
            art_contents.append(article[2] +" "+ article[3])

            art_timestamp.append(article[4])

        return art_ids, art_cates, art_contents, art_timestamp


    @staticmethod
    def PreprocessHistory(art_ids,user_cnt=7560,min_time_seq = 5):
        '''
        获取用户的浏览记录
        :param his_file: 为兼容原始函数，可不使用
        :param art_ids:
        :param min_time_seq:
        :return:
        '''
        art_id = np.asarray(art_ids)
        out_map = {}
        out_art_read = {}
        out_obj = []

        mysql = MysqlConnect()
        user_read_record = mysql.get_member_read_record(user_cnt)
        for each_record in user_read_record:

            userID = int(each_record[0])
            readID = int(each_record[1])
            timestamp = int(each_record[2])
            unreadID = [int(s) for s in each_record[3].split(",")]# 这里的一个误区是 其他系统的推荐信息
            if (len(unreadID)):
                if len(np.where(art_id == readID)[0]): # art_id list中等于 readID的 一维下标
                    readInd = int(np.where(art_id == readID)[0][0]) # 取下标
                    # unreadInd = [int(np.where(art_id == unid)[0][0]) for unid in unreadID if
                    #              len(np.where(art_id == unid)[0]) > 0]
                    # if len(unreadInd): # impression 没有出现在我们的文章库中
                    #     if (userID not in out_map):
                    #         out_map[userID] = []
                    #     out_map[userID] += [(timestamp, readInd, unreadInd)]
                    if (userID not in out_map):
                        out_map[userID] = []
                    out_map[userID] += [(timestamp, readInd)]

            #增加article_id : timestamp 的映射
            if readID not in out_art_read:
                out_art_read[readID] = []
                readIndx =np.where(art_id == readID)
                if len(readIndx)< 1 or len(readIndx[0]) < 1:
                    readInd = -1
                else:
                    readInd = readIndx[0][0]
                out_art_read[readID].append(readInd)
            out_art_read[readID].append(timestamp)

        for userID in out_map.keys():
            #直接略去了900的用户数
            if len(out_map[userID]) > min_time_seq:
                out_map[userID].sort(key=lambda x: x[0]) # 按时间戳排序
                out_obj += [(userID, [timeseq[1] for timeseq in out_map[userID]]),]
        return out_obj,out_art_read
