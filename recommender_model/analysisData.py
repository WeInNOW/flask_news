from Preprocess import Preprocess as Pre
from FilePathPara import *
import pylab as pl

art_ids, art_cats, art_contents,art_timestamp = Pre.PreprocessArticles(NewsDataSetPath)

reader_his,art_his_tim = Pre.PreprocessHistory(HistoryDataSetPath, art_ids)
def get_read_count():
    article_readcount_segment=[]
    for article,value in art_his_tim.items():# 文章的下标
        if value[0] == -1 : # 无这篇文章
            continue
        art_ind = value[0]
        value[0] = art_timestamp[value[0]]
        #if value[0] == 186363919:
        #    break
        #print (value)
        value = [int((value[v] - value[0])/(1000*60*30)) for v in range(len(value))]
        #if value[-1] < 6:#小于7个时间段的不进行计算 - 在后面再说
        #    continue
        #freq = [0] * (value[-1]+2)
        freq = [0] * 49
        #freq[0] = art_ids[art_ind]
        freq[0] = value[-1] + 1 # 表示有效长度
        step = value[1] + 1
        index = 1
        while index < len(value):
            while index < len(value) and value[index] + 1 == step:
                freq[step] += 1
                index += 1
            if index < len(value):
                step = value[index] + 1

        article_readcount_segment.append(freq)
    return article_readcount_segment


    #画图用
    #indexs = [i for i in range(1,len(freq))]
    #print(indexs)
    #pl.plot(indexs,freq[1:],'ob-')
    #pl.show()
    #break
with open('news_content','w',encoding='utf-8') as f:
    for art_content in art_contents:
        art_content = art_content.replace('\n',' ')
        f.write(art_content)
        f.write('\n')
