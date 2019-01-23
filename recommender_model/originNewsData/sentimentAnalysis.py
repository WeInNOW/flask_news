from collections import defaultdict
import os,sys
import re
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
sys.path.append("..")
from Preprocess import Preprocess


def readfile(filename):
    fh=open(filename,'r',encoding='utf-8')
    data=[]
    for x in fh.readlines():
        if(x.strip()!=''):
            data.append(x.strip())
    fh.close()
    return data

#print(x)

#分词处理
'''
def cut2wd(sentence):
    wdlist=jieba.cut(sentence)
    wdrst=[]
    for w in wdlist:
        wdrst.append(w)
    stopwds=readfile("C:/Users/yyq/Desktop/毕业论文/停用词表.txt")
    newwd=[]
    for w2 in wdrst:
        if w2 in stopwds:
            continue
        else:
            newwd.append(w2)
    return newwd


a=cut2wd("我爱北京天安门")
#print(a)
'''

# 去停用词
def cut2wd(sentence):
    wdlist = re.split("[ |,|.|;|:|?|\\t]+",sentence)#
    stopwds = readfile("./wordData/stopWords.txt")
    newwd=[]
    for w in wdlist:
        if w.lower() in stopwds:
            continue
        newwd.append(w)
    return newwd


#词频统计
def Count(words):
    #{"词语"：词频，}
    corpus=words
    vectorizer=CountVectorizer(token_pattern="\\b\\w+\\b")#该类会将文本中的词语转换为词频矩阵，矩阵元素a[i][j] 表示j词在i类文本下的词频
    transformer=TfidfTransformer(norm=None,use_idf=False)#该类会统计每个词语的tf-idf权值
    tf=transformer.fit_transform(vectorizer.fit_transform(corpus)) #第一个fit_transform是计算tf-idf，第二个fit_transform是将文本转为词频矩阵
    word=vectorizer.get_feature_names()#获取词袋模型中的所有词语
    weight=tf.toarray()#将tf-idf矩阵抽取出来，元素a[i][j]表示j词在i类文本中的tf-idf权重
    #print(weight)
    mycp={}
    for i in range(len(weight)):
        for j in range(len(word)):
            mycp.update({str(word[j]):int(weight[i][j])})
    return mycp

#b=Count(["我","爱","天安门","爱","明月"])
#print(b)

#分割字符串为单词，并保存权重
def splitNews(wordline):
    worddict=defaultdict()
    for s in wordline:
        values=s.split('\t')
        word = values[0].split("|")
        worddict[word[0]] =float(values[1])
        if len(word) >= 3:
            for w in values[2].split(","):
                worddict[w] = float(values[1])
    return worddict

def pre_sentiment(wddict):
    neglist=readfile("wordData/word_neg.txt")
    poslist=readfile("wordData/word_pos.txt")

    negdict=splitNews(neglist) # 获取正向词汇与负向词汇及其程度
    posdict=splitNews(poslist)

    notlist=readfile("wordData/notword.txt")
    notwd=set()

    for s in notlist:
        notwd.add(s)
    return negdict,posdict,notwd

#情感得分计算
def score(negdict,posdict,notwd,wddict):
    negscore=0.0
    posscore=0.0

    w = 1
    for word in wddict:

        if word in negdict.keys():
            negscore+=w*float(negdict[word]) #*wddict[word]
            if w == -1 :
                w = 1
        elif word in posdict.keys():
            posscore +=w*float(posdict[word]) #*wddict[word]
            if w == -1:
                w = 1
        elif word in notwd:
            w *= -1
    return negscore,posscore

str1="Ich mag diese Art von Arbeit, was  ist mit dir??"
cut=cut2wd(str1)
print(cut)
#wddict=Count(cut)
#senwd,notwd,degreewd=pos(wddict)
#rst=score(senwd,notwd,degreewd)
#print(rst)


art_ids, art_cates, art_contents,art_timestamp = Preprocess.PreprocessArticles("./ArticleRecord.txt")
#批量测试
for thisfile in art_contents:
    print(thisfile)
    cut=cut2wd(art_contents)
    wddict=Count(cut)
    #senwd,notwd,degreewd=pos(wddict)
    posdict, negdict, notwd = pre_sentiment(wddict)
    negscore,posscore=score(posdict,negdict,notwd,wddict)
    print(negscore,posscore)
