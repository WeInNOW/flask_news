# coding:utf-8
import re
from bs4 import BeautifulSoup


class HtmlParser(object):

    def parser(self, page_url, html_cont):
        if page_url is None or html_cont is None:
            return
        soup = BeautifulSoup(html_cont, 'html.parser', from_encoding='utf-8')
        new_urls = self._get_new_urls(page_url, soup)
        new_data = self._get_new_comments(page_url, soup)
        return new_urls, new_data

    def _get_new_urls(self, page_url, soup):
        new_urls = set()

        comments_count = str(soup.find(id='total-comments').string).encode('utf-8')
        c = int(re.findall(r"\d+", comments_count)[0])

        if c > 0:
            for i in range(c / 20):
                new_urls.add(page_url + '/hot?p=' + str(i + 2))

        # links = soup.find_all('a',href=re.compile(r'/subject/\d*/$'))
        # #TODO: 如果links是None那么有可能报NoneType is not iterable
        # for link in links:
        #     new_url = link['href']
        #     new_full_url = urlparse.urljoin(page_url,new_url)
        #     new_urls.add(new_full_url)
        return new_urls

    # 这个是解析新闻主页的
    def _get_new_data(self, page_url, soup):
        data = {}
        try:
            data['book_id'] = page_url.split('/')[-2]
            data['list'] = []
            comments = soup.find(id='comments', class_='comment-list hot show').find_all('li')
            for child in comments:
                child_list = {}
                # user_id
                if child.find('a', href=re.compile(r'people')):
                    child_list['user_id'] = child.find('a', href=re.compile(r'people'))['href'].split('/')[-2]
                else:
                    child_list['user_id'] = ''

                # user_name
                if child.find('a', href=re.compile(r'people')):
                    child_list['user_name'] = child.find('a', href=re.compile(r'people')).get_text()
                else:
                    child_list['user_name'] = ''

                # user_rating
                if child.find('span', class_='rating'):
                    child_list['rating'] = child.find('span', class_='rating')['title']
                else:
                    child_list['rating'] = ''

                if child.find(text=re.compile(r'\d*-\d*-\d')):
                    child_list['time'] = child.find(text=re.compile(r'\d*-\d*-\d'))
                else:
                    child_list['time'] = ''

                if child.find(class_='comment-content'):
                    child_list['comment'] = child.find(class_='comment-content').get_text()
                else:
                    child_list['comment'] = ''
                data['list'].append(child_list)
        except Exception as e:
            print
            e
        return data