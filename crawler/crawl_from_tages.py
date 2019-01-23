# coding:utf-8

import urllib.request
import re
import time
from datetime import date
from bs4 import BeautifulSoup
from mySqlBase import MysqlConnect
from distutils.filelist import findall


def get_soup(source_url):
    """
    返回解析器
    :param source_url:
    :return:
    """

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}

    req = urllib.request.Request(source_url, headers= headers)
    page = urllib.request.urlopen(req)
    contents = page.read()
    # print(contents)
    soup = BeautifulSoup(contents, "html.parser")

    return soup


def crawl_news():
    source_url = 'https://www.tagesspiegel.de/'
    soups = get_soup(source_url)
    available_tags = []
    available_tags.extend(soups.find_all('li', class_='hcf-teaser'))
    available_tags.extend(soups.find_all('li', class_='hcf-teaser hcf-left'))
    available_tags.extend(soups.find_all('li', class_='hcf-teaser hcf-left hcf-last'))
    url_list = []
    for tag in available_tags:

        # m_name = tag.find('span', class_='title').get_text()
        # m_rating_score = float(tag.find('span', class_='rating_num').get_text())
        # m_people = tag.find('div', class_="star")
        # m_span = m_people.findAll('span')
        # m_peoplecount = m_span[3].contents[0]
        try:
            m_url = tag.find('a').get('href')
        except Exception as e:
            # print(tag)
            continue
        if m_url.find('http') > -1:
            continue
        # print(m_name + "        " + str(m_rating_score) + "           " + m_peoplecount + "    " + m_url)
        url_list.append(source_url + m_url)
        #print(m_url)

#        break
    category_dict = {'kultur': 13845, 'sport': 13839, 'berlin': 2215224, 'studiu': 2215199,
                     'themen': 2215339, 'weltspiegel': '2215200', 'wirtschaft': 13836, 'wissen': 13838,
                     'zeitun': 2215229, 'meinun': 13837, 'mediacenter': 2215194, 'medien': 13843,
                     'berlin': 13840, 'mediac': 2215194, 'mobil': 2215248, 'politil': 13841}
    # img_urls = []
    # titles = []
    # datetimes = []
    # texts = []
    # contents = []
    # categorys = []
    for url in url_list:
        # print(url)
        # 获取类别
        words = re.split('/', url)
        category = 0
        if len(words) > 4:
            category = words[3]
            if category in category_dict.keys():
                category = category_dict.get(category)
            else:
                category = 0
        try:
            soup = get_soup(url)
            # 获取图像url
            tag = soup.find('div', class_='ts-media')
            img_url = source_url + tag.find('img').get('src')
            # print(img_url)

            # 获取标题
            tag = soup.find('h1', class_='ts-title')
            title = tag.find('span', class_='ts-headline').get_text().strip()
            title = title.replace("'","_")
            # print(title)

            # 获取时间和标题
            tag = soup.find('header', class_='ts-article-header')
            update_time = tag.find('div', class_='ts-meta').find('time').get('datetime')
            update_date = update_time[:-6]
            # print(update_date)
            timestamp = int(time.mktime(time.strptime(update_date, '%Y-%m-%dT%H:%M:%S')))
            text = tag.find('p', class_='ts-intro').get_text()
            text = text.replace("'","_")
            # print(text)

            # 获取段落内容
            tag = soup.find('div', class_='ts-article-content').find('div',class_='ts-article-body')
            content = ''
            segment_cnt = 0
            for segment in tag.find_all('p'): # 获得3段就ok了
                if segment_cnt > 2:
                    break
                # print(segment.get_text())
                content += segment.get_text() + '\n'  # 获取所有的段落内容
                segment_cnt += 1
            content = content.replace("'","_")
        except Exception as e:
            print(e)
            continue
        # titles.append(title)
        # texts.append(text)
        # datetimes.append(update_date)
        # img_urls.append(source_url + img_url)
        # contents.append(content)
        # categorys.append(category)

        mysql = MysqlConnect()
        query = '''
        select count(1) from crawl_article_info_online
        where article_url ='%s';
    ''' % (url)
        datas = mysql.select(query)
        if datas[0][0] == 1:  # 已经被填充过了
            continue

        query = '''
        insert into crawl_article_info_online(article_url,img_url,title,text,create_date,update_date,segments,category_id,time_stamp) 
        values ('%s','%s','%s','%s','%s','%s','%s',%s,%s);
    ''' % (url, img_url, title, text,str(date.today()),update_date, content, category, timestamp)

        mysql.exec(query)  # 插入数据


if __name__ == '__main__':
    crawl_news()
