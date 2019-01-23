# coding:utf-8
import requests
import time
import json
class HtmlDownloader(object):

    def __init__(self):
        self.index = 0
        self.mogu_index = -1
        self.headers = {
            'Accept': 'text/html, application/xhtml+xml, image/jxr, */*',
            'Accept-Language': 'zh-Hans-CN, zh-Hans; q=0.5',
            'Connection': 'Keep-Alive',
            'Cookie': 'bid=lkpO8Id/Kbs; __utma=30149280.1824146216.1438612767.1440248573.1440319237.13; __utmz=30149280.1438612767.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); as=http://book.douban.com/people/133476248/; ll=108288; viewed=26274009_1051580; ap=1; ps=y; ct=y; __utmb=30149280.23.10.1440319237; __utmc=30149280; __utmt_douban=1; _pk_id.100001.3ac3=b288f385b4d73e38.1438657126.3.1440319394.1440248628.; __utma=81379588.142106303.1438657126.1440248573.1440319240.3; __utmz=81379588.1440319240.3.2.utmcsr=movie.douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/; _pk_ses.100001.3ac3=*; __utmb=81379588.23.10.1440319240; __utmt=1; __utmc=81379588; _pk_ref.100001.3ac3=%5B%22%22%2C%22%22%2C1440319240%2C%22http%3A%2F%2Fmovie.douban.com%2F%22%5D',
            'Host': 'book.douban.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.10240'}

    # 返回有效的ip的地址
    def get_proxy(self):

        r = requests.get('http://127.0.0.1:8000/?types=2')
        ip_ports = json.loads(r.text)
        self.index = self.index + 1

        ip = ip_ports[self.index][0]
        port = ip_ports[self.index][1]

        headers = {'User-Agent': 'Mozilla/4.0 (compatible;MSIE 5.5;Windows NT', 'Connection': 'close'}
        proxies = {
            'http': 'http://%s:%s' % (ip, port),
            'https': 'http://%s:%s' % (ip, port)
        }

        while self.index < 100:
            try:
                r = requests.get('http://www.baidu.com', headers=self.headers, proxies=proxies, timeout=5)
                return proxies
            except Exception as e:
                self.index= self.index + 1
                ip = ip_ports[self.index][0]
                port = ip_ports[self.index][1]
                proxies = {
                    'http': 'http://%s:%s' % (ip, port),
                    'https': 'http://%s:%s' % (ip, port)
                }

        print("已达到100次代理尝试")

    def get_mogu_proxy(self):
        self.mogu_index = self.mogu_index + 1

        proxy_list = [{"port": "35117", "ip": "182.42.43.76"}, {"port": "34380", "ip": "113.124.92.128"},
                              {"port": "38103", "ip": "115.221.126.238"}, {"port": "32436", "ip": "100.67.39.254"},
                              {"port": "47219", "ip": "125.86.167.191"}, {"port": "41396", "ip": "222.221.41.67"},
                              {"port": "40269", "ip": "220.186.142.110"}, {"port": "23529", "ip": "27.29.156.196"},
                              {"port": "41105", "ip": "220.165.29.228"}, {"port": "39996", "ip": "36.33.25.135"},
                              {"port": "44740", "ip": "117.91.209.254"}, {"port": "20657", "ip": "49.88.88.160"},
                              {"port": "46327", "ip": "106.57.22.136"}, {"port": "22581", "ip": "114.226.241.215"},
                              {"port": "40931", "ip": "101.27.20.229"}, {"port": "42645", "ip": "60.177.228.16"},
                              {"port": "46979", "ip": "58.19.80.25"}, {"port": "41242", "ip": "1.29.109.106"},
                              {"port": "49276", "ip": "58.218.92.176"}, {"port": "23959", "ip": "49.84.121.33"},
                              {"port": "26437", "ip": "60.182.164.26"}, {"port": "42176", "ip": "115.208.14.19"},
                              {"port": "20581", "ip": "117.63.227.244"}, {"port": "41840", "ip": "117.85.106.193"},
                              {"port": "48250", "ip": "117.67.140.22"}, {"port": "45457", "ip": "42.4.217.227"},
                              {"port": "40207", "ip": "36.25.42.190"}, {"port": "33339", "ip": "180.122.150.139"},
                              {"port": "33151", "ip": "116.248.187.125"}, {"port": "40809", "ip": "114.226.89.245"}]
        ip = proxy_list[self.mogu_index]['ip']
        port = proxy_list[self.mogu_index]['port']
        proxies = {
            'http': 'http://%s:%s' % (ip, port),
            # 'https': 'http://%s:%s' % (ip, port)
        }
        return proxies


    def download(self,url):
        if url is None:
            return None

      #  headers = {'User-Agent': 'Mozilla/4.0 (compatible;MSIE 5.5;Windows NT','Connection': 'close'}
      #  headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'}
        headers = head= {
   'Accept':'text/html, application/xhtml+xml, image/jxr, */*',
   'Accept-Language': 'zh-Hans-CN, zh-Hans; q=0.5',
   'Host':'book.douban.com',
   'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.10240'}
        # 头信息

        self.proxies = self.get_mogu_proxy()

        #如果去掉这句话就变成了不使用代理
        while True:
            try:
                s = requests.session()
                s.keep_alive = False
                r = requests.get(url, headers=headers, proxies=self.proxies, timeout=20)
                if r.status_code == 200:
                    r.encoding = 'utf-8'
                    if r.text.encode('unicode-escape').decode('string_escape').find("Unauthorized") != -1:
                        raise RuntimeError(r.text.encode('unicode-escape').decode('string_escape'))
                    return r.text
                else:
                    raise RuntimeError('得不到正确得代理，从新找代理')

            except Exception as e:
                self.proxies = self.get_mogu_proxy()
                time.sleep(5)


        return None
