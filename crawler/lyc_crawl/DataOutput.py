# encoding:utf-8
import codecs
import pymysql
import time
class DataOutput(object):
    def __init__(self):
        self.datas=[]
        self.conn = pymysql.connect(host='39.106.39.216',
                               user='root',
                               passwd="admin123",
                               db='doubandb',
                               port=3306,
                               charset='utf8')
        self.cursor = self.conn.cursor()

    def store_data(self,data):
        if data is None:
            return
        self.datas.append(data)

    def output_html(self):
        fout = codecs.open('baike.html','w',encoding='utf-8')
        fout.write("<html>")
        fout.write("<body>")
        fout.write("<table>")
        for data in self.datas:
            fout.write("<tr>")
            fout.write("<td>%s<td>"%data['url'])
            fout.write("<td>%s<td>"%data['title'])
            fout.write("<td>%s<td>"%data['summary'])
            fout.write("</tr>")
        fout.write("<html>")
        fout.write("<body>")
        fout.write("<table>")
        fout.close()

    def store_into_database(self,alldata):
        try:
            book_id = alldata['book_id']
            datas = alldata['list']
            for data in datas:
                book_data = "'%s','%s','%s','%s','%s','%s','%s',%d " % (data['user_id'], data['user_name'].replace("'", "\\\'"), data['rating'], data['comment'], book_id , data['time'],data['user_img'],int(data['valid_count']))
                user_sql = 'INSERT INTO user_book_rating_new (user_id,user_name,rating,comment,book_id,rate_time,user_img,valid_count) VALUES(' + book_data + ');'
                self.cursor.execute(user_sql)
                self.conn.commit()
        except Exception as e:
            print(e)

    def get_new_book_id_index(self,start_index):
        try:
            user_sql = 'SELECT * FROM `valid_index` ORDER BY time DESC'
            self.cursor.execute(user_sql)
            results = self.cursor.fetchall()
            index = results[0]['index']
        except Exception as e:
            print(e)
        return index

    def get_new_book_id_index(self,target_index):
        try:
            index_data = "%s,'%s'"%(target_index,time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
            user_sql = 'INSERT INTO valid_index (bindex, btime) VALUES' + index_data + ');'
            self.cursor.execute(user_sql)
            self.conn.commit()
        except Exception as e:
            print(e)