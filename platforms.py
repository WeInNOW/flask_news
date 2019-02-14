# encoding: utf-8
import pymysql
import time
import datetime
from sqlalchemy import func
from sqlalchemy.sql.functions import current_time

from crawl_from_tages import crawl_news
from recommender_model.Runtime import getRecommender
from redis_con import redis_connect

pymysql.install_as_MySQLdb()  # mysqldb python3 之后不在支持
from flask import Flask, render_template, request, redirect, url_for, session, current_app
import config
from models import RsAtricleInfo, RsMemberDetail, RsMemberHistory, CrawlArticleInfoOnline, CategoryDict, \
    ArticleInteraction
from exts import db
from decorators import login_required
from sqlalchemy import or_

app = Flask(__name__)
app.config.from_object(config)
db.init_app(app)


@app.route('/')
def index():
    categorys = CategoryDict.query.all()
    category_dict = {}
    for category in categorys:
        category_id = category.category_id
        label = category.label
        category_dict[category_id] = label

    context = {
        'popularity_articles': CrawlArticleInfoOnline.query.order_by(CrawlArticleInfoOnline.update_date.desc()).limit(4),
        'recent_articles': CrawlArticleInfoOnline.query.order_by(CrawlArticleInfoOnline.update_date.desc()).limit(9),
        'hot_articles': CrawlArticleInfoOnline.query.filter(CrawlArticleInfoOnline.time_stamp >= (time.time() - 3600 * 96))
        .order_by(CrawlArticleInfoOnline.read_cnt.desc()).limit(9),
        'category_dict': category_dict
    }
    return render_template('index.html', **context)


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        username = request.form.get('username')
        password = request.form.get('password')
        user = RsMemberDetail.query.filter(RsMemberDetail.username == username, RsMemberDetail.password ==
                                           password).first()
        if user:
            session['user_id'] = user.user_id
            # 如果想在31天内都不需要登录
            session.permanent = True
            return redirect(url_for('index'))
        else:
            return u'用户名或者密码错误，请确认好重新登录'


'''
注册方法先不给使用
'''


@app.route('/regist/', methods=['GET', 'POST'])
def regist():
    if request.method == 'GET':
        return render_template('regist.html')
    else:
        telephone = request.form.get('telephone')
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        # 手机号码验证，如果被注册了就不能用了
        user = RsMemberDetail.query.filter(RsMemberDetail.username == username).first()
        if user:
            return u'该手机号码被注册，请更换手机'
        else:
            # password1 要和password2相等才可以
            if password1 != password2:
                return u'两次密码不相等，请核实后再填写'
            else:
                user = RsMemberDetail(username=username, password=password1)
                db.session.add(user)
                db.session.commit()
                # 如果注册成功，就让页面跳转到登录的页面
                return redirect(url_for('login'))


# 判断用户是否登录，只要我们从session中拿到数据就好了   注销函数
@app.route('/logout/')
def logout():
    # session.pop('user_id')
    # del session('user_id')
    session.clear()
    return redirect(url_for('login'))


@app.route('/question/', methods=['GET', 'POST'])
@login_required
def question():
    if request.method == 'GET':
        return render_template('question.html')
    else:
        title = request.form.get('title')
        content = request.form.get('text')
        question = RsAtricleInfo(title=title, content=content)
        user_id = session.get('user_id')
        user = RsMemberDetail.query.filter(RsMemberDetail.user_id == user_id).first()
        # question.author = user
        db.session.add(question)
        db.session.commit()
        return redirect(url_for('index'))


@app.route('/recommender/', methods=['GET', 'POST'])
@login_required
def recommender():
    user_id = session.get('user_id')
    impressions = getRecommender(user_id)
    # impression = db.session.query(RsMemberHistory.impression).filter(RsMemberHistory.member_id == user_id).order_by(RsMemberHistory.time_stamp).first()
    # 直接就是推荐表
    # impressions = impression[0].split(',')
    # app.logger.warning(impressions)

    context = {
        'articles': CrawlArticleInfoOnline.query.filter(CrawlArticleInfoOnline.article_id.in_(impressions)).order_by(
            CrawlArticleInfoOnline.update_date),
        'name': '推荐'
    }
    return render_template('category_label.html', **context)


@app.route('/timeline/', methods=['GET', 'POST'])
# @login_required # 暂时不需要
def timeline():
    """

    :return:
    """
    # lastdate = db.session.query(CrawlArticleInfoOnline.create_date).order_by(CrawlArticleInfoOnline.create_date.desc()).first()
    # lastdate = db.session.query(func.date_format(CrawlArticleInfoOnline.create_date, '%Y-%m-%d')).order_by(CrawlArticleInfoOnline.create_date.desc()).first()
    # app.logger.warning(str(lastdate))
    # app.logger.warning(type(lastdate))
    # app.logger.warning(date.today())

    # app.logger.warning('*****error')
    user_id = session.get('user_id')

    context = {
        'articles': CrawlArticleInfoOnline.query.order_by(CrawlArticleInfoOnline.update_date.desc()).limit(20)
    }
    # 同时记录到表中
    return render_template('timeline.html', **context)

@app.route('/hot_articles/', methods=['GET', 'POST'])
# @login_required # 暂时不需要
def hot_articles():
    """
    # 找近三天的数据
    :return:
    """
    context = {
        'articles': CrawlArticleInfoOnline.query.filter(CrawlArticleInfoOnline.time_stamp >= (time.time() - 3600 * 96))
        .order_by(CrawlArticleInfoOnline.read_cnt.desc()).limit(20),
        'name': '热门'
    }
    # 同时记录到表中
    return render_template('category_label.html', **context)


@app.route('/category_label/<name>/')
def category_label(name):
    context = {
        'articles': CrawlArticleInfoOnline.query.filter(CrawlArticleInfoOnline.category == name).
        order_by(CrawlArticleInfoOnline.update_date.desc()),
        'name': name
    }
    return render_template('category_label.html', **context)


@app.route('/detail/<article_id>/')
def detail(article_id):
    """
    需要加入到redis中，缓存用户信息
    key:user_id member:article_id score:timestamp
    如果有重复的点击在后面加上_timestamp作为member
    :param article_id:
    没有登录的情况记录什么？
    :return:
    """
    user_id = session.get('user_id')
    if user_id is not None:
        redis_cli = redis_connect()  # 是不是应该在session中保留该对象，多出都会使用到吗？
        t = time.time()
        timestamp = int(round(t * 1000))  # 获取时间戳
        redis_cli.add_user_event(user_id, article_id, timestamp)

    article_model = CrawlArticleInfoOnline.query.filter(CrawlArticleInfoOnline.article_id == article_id).first()
    # 获取相似文章id 从表中获取吧；需要多表查询
    relate_article_index = db.session.query(ArticleInteraction.sim_article_1, ArticleInteraction.sim_article_2,
                                            ArticleInteraction.sim_article_3, ArticleInteraction.sim_article_4,
                                            ArticleInteraction.sim_article_5).filter(
        ArticleInteraction.article_id == article_id).first()
    relate_articles = []  # 可以先设一个默认选项： 暂无相似文章
    if relate_article_index is not None:
        for article_index in relate_article_index:
            if article_index is None:
                break
            article_tuple = CrawlArticleInfoOnline.query.filter(CrawlArticleInfoOnline.article_id == article_index).first()
            relate_articles.append(article_tuple)

    return render_template('detail.html', article=article_model,
                           relate_articles=relate_articles, )


@app.route('/timeline_detail/<article_id>/')
def timeline_detail(article_id):
    article_model = CrawlArticleInfoOnline.query.filter(CrawlArticleInfoOnline.article_id == article_id).first()
    # 获取最热和最相似的几篇文章
    return render_template('detail.html', article=article_model, relate_news_list=[], most_freq_news_list=[])


@app.route('/add_read_history/', methods=['POST'])
@login_required
def add_readhistory():
    content = request.form.get('article_content')
    article_id = request.form.get('article_id')
    answer = RsMemberHistory(article_id=article_id)
    user_id = session['user_id']
    user = RsMemberDetail.query.filter(RsMemberDetail.id == user_id).first()
    # answer.author = user
    question = RsAtricleInfo.query.filter(RsAtricleInfo.article_id == article_id).first()
    answer.question = question
    db.session.add(answer)
    db.session.commit()
    return redirect(url_for('detail', article_id=article_id))


@app.route('/search/')
def search():
    q = request.args.get('q')  # 查找不能有空格，否则会以加号隔开，找不到
    # title, content
    # 或 查找方式（通过标题和内容来查找）
    # questions = Question.query.filter(or_(Question.title.contains(q),
    #                                     Question.content.constraints(q))).order_by('-create_time')
    # 与 查找（只能通过标题来查找）

    app.logger.warning(q)
    questions = RsAtricleInfo.query.filter(or_(RsAtricleInfo.title.contains(q), RsAtricleInfo.text.contains(q)))
    return render_template('category_label.html', name='检索', articles=questions)


# 钩子函数(注销)
@app.context_processor
def my_context_processor():
    user_id = session.get('user_id')
    if user_id:
        user = RsMemberDetail.query.filter(RsMemberDetail.user_id == user_id).first()
        if user:
            return {'user': user}
    return {}


if __name__ == '__main__':
    app.run(debug=True)
