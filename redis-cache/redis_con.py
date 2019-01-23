#!/usr/bin/env python
# -*- coding:utf8 -*-

import redis
import time
import datetime
'''
这种连接是连接一次就断了，耗资源.端口默认6379，就不用写 没有
r = redis.Redis(host='127.0.0.1',port=6379)
r.set('name','root')

print(r.get('name').decode('utf8'))
'''
'''
连接池：
当程序创建数据源实例时，系统会一次性创建多个数据库连接，并把这些数据库连接保存在连接池中，当程序需要进行数据库访问时，
无需重新新建数据库连接，而是从连接池中取出一个空闲的数据库连接
'''
class redis_connect:

    def __init__(self):
        self.pool = redis.ConnectionPool(host='127.0.0.1')   #实现一个连接池
        self.r = redis.Redis(connection_pool=self.pool)

    '''
    用户是否在集合中，不在的话添加，在的添加用户行为
    setifnotexit
    '''

    '''
    记录用户的行为
    使用zset :  -- 但 member 不能重复，如果点击多个怎么处理,在其后添加
    1) "186583297"
    2) "186583297_1543412711930"
    解析时，先分割后取值
    member ：记录元素值（article_id) 
    score ：timestamp 用于排序
    '''
    def add_user_event(self,userId,articleId,timestamp):
        if self.r.zrank(userId,articleId) is not None and self.r.zrank(userId,articleId) >= 0:
            articleId = str(articleId)+'_'+str(timestamp)
        member2score={articleId:timestamp}
        self.r.zadd(userId,member2score)

    '''
    获取用户的行为数据，
    '''
    def add_articles(self,userId,article_id):
        if self.r.zrank(userId,article_id)>= 0:
            timestamp = time.time()

if __name__ == '__main__':
    redis_cli = redis_connect()
    t = time.time()
    timestamp = int(round(t * 1000))  # 获取时间戳
    print(timestamp)
    redis_cli.add_user_event(1006209,186543551,timestamp)