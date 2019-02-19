# coding:utf-8

import urllib.request
import chardet
import re
import sys
import time
import parse_article
from datetime import date
from bs4 import BeautifulSoup
from mySqlBase import MysqlConnect
from distutils.filelist import findall

category_dict = {'台湾': '港澳台', '财经': '财经', '国际': '国际', '体育': '文体', '视频': '其他', '图片': '其他', '国内': '社会', '社会': '社会',
                 '金融': '财经', '港澳': '港澳台', '文化': '文体', '华人': '国际', '产经': '财经', '娱乐': '其他', '汽车': '社会', '证券': '财经',
                 'I  T': '互联网', '军事': '军事', '葡萄酒': '财经', '能源': '国际', '健康': '社会','房产': '社会'}


def get_soup(source_url):
    """
    返回解析器
    :param source_url:
    :return:
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}

    req = urllib.request.Request(source_url, headers=headers)
    page = urllib.request.urlopen(req, timeout=20)
    contents = page.read()
    contents.decode('GBK')  # 网页编码使用gb2312进行，需要进行调整
    # print(contents)
    soup = BeautifulSoup(contents, "html.parser", from_encoding='GBK')

    return soup


def crawl_news(source_url):
    # 类别直接由
    soups = get_soup(source_url)

    content_tag = soups.find('div', class_='content_list')
    url_list = []
    categorys = []
    time_list = []
    items = content_tag.find_all('li')
    for item in items:
        try:

            m_url = item.find('div', class_='dd_bt').find('a').get('href')[2:]  #
            if m_url.find('www') < 0:
                continue
            category = item.find('div', class_='dd_lm').find('a').get_text().strip()
            categorys.append(category)
            times = item.find('div', class_='dd_time').get_text().strip()
            time_list.append(times)

            url_list.append("http://" + m_url)
        except Exception as e:
            print(e)
            continue

    for index, url in enumerate(url_list):
        print(url)
        # 获取类别 - 输入url
        try:
            category = category_dict.get(categorys[index])
            # print(category)
            if category is None:  # 没有出现的不做考虑
                continue
            # 知道 2月 1号 是： 2-1
            update_date = "2019-0" + time_list[index].replace(" ", "T")
            print(update_date)
            timestamp = int(time.mktime(time.strptime(update_date, '%Y-%m-%dT%H:%M')))
            img_url, title, text = get_news_property(url)
            if len(text.strip()) < 3:
                continue
        except Exception as e:
            print(e)
            continue
        # titles.append(title)
        # texts.append(text)
        # datetimes.append(update_date)
        # img_urls.append(source_url + img_url)
        # contents.append(content)
        # categorys.append(category)

        exec_sql_result = insert_into_sql(url, img_url, title, text, update_date, category, timestamp)

        if exec_sql_result == 1:
            break


def insert_into_sql(url, img_url, title, text, update_date, category, timestamp):
    mysql = MysqlConnect()
    query = '''
    select count(1) from crawl_article_info_online
    where article_url ='%s';
    ''' % url
    datas = mysql.select(query)
    if datas[0][0] == 1:  # 已经被填充过了
        return 1  # 表示当前的已经被填充过了，可以等一段时间再次爬取
    query = """
    insert into crawl_article_info_online(article_url,img_url,title,text,create_date,update_date,category,time_stamp) 
    values ('%s','%s','%s','%s','%s','%s','%s',%s);
    """ % (url, img_url, title, text, str(date.today()), update_date, category, timestamp)

    try:
        mysql.exec(query)
    except Exception as e:
        print(e)  # 应写一个日志
        return -1
    return 0  # 写入返回并返回


def get_news_property(url):
    """
    这一段解析是没有问题的
    :param url:
    :return:
    """
    soup = get_soup(url)
    # 获取标题
    tag = soup.find('div', class_='content')
    title = tag.find('h1').get_text().strip()
    # print(title.encode('gb2312'))

    # # 获取时间
    # raw_date = tag.find('div', class_='left-time').find('div', class_='left-t').get_text().strip()
    # date_zn = raw_date.encode('utf-8')
    # # can't concat str to bytes
    # update_date = date_zn[:4] + "-" + date_zn[5:7] + "-" + date_zn[8:10] + "T" + date_zn[12:17]
    # print(update_date)
    # timestamp = int(time.mktime(time.strptime(update_date, '%Y-%m-%dT%H:%M')))
    # 获取图像url
    contents = soup.find('div', class_='left_zw')
    try:
        img_url = contents.find('img').get('src')  # 若不能正常获取img_url 返回
    except Exception as e:
        raise e

    content = ''
    text_len = 100
    if len(img_url) < 1:
        text_len += 100
    segment_cnt = 0
    [s.extract() for s in tag('script')]  # 去除指定script的内容
    for segment in tag.find_all('p'):  # 获得2段就ok了
        if segment_cnt > 2 and len(content) > text_len:
            break
        # print(segment.get_text())
        content += segment.get_text().strip('\n') + '\n'  # 获取相关的
        segment_cnt += 1
    content = content.replace("'", "_")

    return img_url, title, content


def drop():
    source_url = 'http://www.chinanews.com/'
    # 类别直接由
    soups = get_soup(source_url)
    available_tags = []
    available_tags.extend(soups.find_all('div', class_='w1000 mt10'))
    url_list = []
    for tag in available_tags:
        # 取tag的全部内容，然后直接解析url吧
        raw_text = str(tag)
        pattern = '(https?://[^\s)";]+(\.(\w|/)*))'
        link = re.compile(pattern).findall(raw_text)


def temp_task():
    for key, val in category_dict.items():
        sql = "insert into category_dict(`category_id`, `label`) values(%s, '%s');" % (val, key)
        print(sql)


if __name__ == '__main__':
    # 爬最近的n个页面 - 过滤没有图片的文章
    for i in range(1, 8):
        source_url = 'http://www.chinanews.com/scroll-news/news' + str(i) + '.html'
        crawl_news(source_url)
    # parse_article.sim_article_parse_update()
