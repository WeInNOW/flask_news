#encoding: utf-8

from exts import db
from datetime import datetime

class RsMemberDetail(db.Model):
    __tablename__ = 'member_detail'
    user_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    username = db.Column(db.String(32), nullable=False)
    password = db.Column(db.String(32), nullable=False)
    nickname = db.Column(db.String(32))
    telephone = db.Column(db.String(11))
    gender = db.Column(db.Integer)
    del_flag = db.Column(db.String(1))


class CategoryDict(db.Model):
    __tablename__ = 'category_dict'
    category_id = db.Column(db.INT, primary_key=True,)
    label = db.Column(db.String(128), nullable=False)
    create_date = db.Column(db.DateTime)


class RsAtricleInfo(db.Model):
    __tablename__ = 'rs_article_info'
    article_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    article_url = db.Column(db.String(256))
    img_url = db.Column(db.String(256))
    title = db.Column(db.String(128))
    text = db.Column(db.Text)
    segments = db.Column(db.Text)
    create_date = db.Column(db.DateTime)
    update_date = db.Column(db.DateTime)
    time_stamp = db.Column(db.BigInteger, nullable=False)
    domain_id = db.Column(db.Integer)
    category_id = db.Column(db.Integer)


class RsMemberHistory(db.Model):
    __tablename__ = 'rs_member_history'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    member_id = db.Column(db.BigInteger,nullable=False)  # , db.ForeignKey('rs_member_detail.id')
    article_id = db.Column(db.BigInteger,nullable=False)
    # question = db.relationship('Question', backref=db.backref('answers', order_by=id.desc()))
    time_stamp = db.Column(db.BigInteger, nullable=True)
    impression = db.Column(db.String(256))


class CrawlArticleInfoOnline(db.Model):
    __tablename__ = 'crawl_article_info_online'
    article_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    article_url = db.Column(db.String(1024))
    img_url = db.Column(db.String(1024))
    title = db.Column(db.String(256))
    text = db.Column(db.Text)
    create_date = db.Column(db.DateTime)
    update_date = db.Column(db.DateTime)
    time_stamp = db.Column(db.BigInteger, nullable=False)
    domain_id = db.Column(db.Integer)
    category = db.Column(db.String(128))
    read_cnt = db.Column(db.Integer)


class ArticleInteraction(db.Model):
    __tablename__ = 'article_interaction'
    article_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    read_cnt = db.Column(db.Integer)
    sim_article_1 = db.Column(db.Integer)
    sim_article_1_score = db.Column(db.Float)
    sim_article_2 = db.Column(db.Integer)
    sim_article_2_score = db.Column(db.Float)
    sim_article_3 = db.Column(db.Integer)
    sim_article_3_score = db.Column(db.Float)
    sim_article_4 = db.Column(db.Integer)
    sim_article_4_score = db.Column(db.Float)
    sim_article_5 = db.Column(db.Integer)
    sim_article_5_score = db.Column(db.Float)


class PopularestArticle(db.Model):
    __tablename__ = 'popularest_articles'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    article_id = db.Column(db.BigInteger,)
    popular_score = db.Column(db.Integer)
    create_date = db.Column(db.DateTime)


class MemberReadEvent(db.Model):
    __tablename__ = 'member_read_event'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    member_id = db.Column(db.BigInteger, nullable=False)  # db.ForeignKey('rs_member_detail.id')
    article_id = db.Column(db.BigInteger, nullable=False)
    # question = db.relationship('Question', backref=db.backref('answers', order_by=id.desc()))
    time_stamp = db.Column(db.BigInteger, nullable=True)
    impression = db.Column(db.String(256))  # 推荐项目

