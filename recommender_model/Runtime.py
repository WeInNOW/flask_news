import jieba
import torch
import torch.nn as nn
import torch.optim as optim
import pandas as pd
import random as rand
import math
import json as js
import numpy as np
from Preprocess import Preprocess as Pre
import AutoEncoder as AE
from RNN import GRU, Recommend
from tkinter import *
import codecs
import time
from GeneralPara import *
from FilePathPara import *
from popular_recommender.popularity_recommendation import generate_recommender_list
# art_ids, art_cats, art_contents = Pre.PreprocessArticles(NewsDataSetPath, True)
from preProcess_sql import PreProcess_sql
# art_ids, art_cats, art_contents, art_timestamp = PreProcess_sql.PreprocessArticles()
art_ids, art_cats, raw_words, art_timestamp = PreProcess_sql.PreprocessArticles()
art_contents = []  # 记录文章直接的切分词语，已去除了英文和数字
for art_content in raw_words:
    art_content.replace("\n", "")
    article_word = ' '.join(jieba.cut(art_content))
    art_contents.append(re.sub('[a-zA-Z0-9.。:：,，)）(（！!?”“\"]', '', article_word))  # 去除英文和数字

tokens = Pre.Tokenize(art_contents, StopWordPath)
token_freq, max_freq = Pre.CountToken(tokens)
norm_freq = Pre.Normalize(token_freq, max_freq)
filtered_art_index = Pre.MinCountClip(tokens, 5)
art_use_ids = [art_ids[index] for index in filtered_art_index]
art_cats = [art_cats[index] for index in filtered_art_index]
art_norm_freq = [norm_freq[index] for index in filtered_art_index]
encoder = AE.AutoEncoder()
encoder.load(AutoEncoderSavePath+"7558.net")
art_encoded = encoder.encodeNorm(torch.Tensor(art_norm_freq))
user_repre = js.load(open(UserStatePath, "r"))
for user_id in user_repre:
    user_state = torch.unsqueeze(torch.Tensor(user_repre[user_id][0]), 0)
    con_state = torch.unsqueeze(torch.Tensor(user_repre[user_id][1]), 0)
    user_repre[user_id] = (user_state, con_state)
for i in range(len(art_contents)):
    art_contents[i] = art_contents[i].replace("\n", " ")

output_file = codecs.open(RecommendedPath, "w", "utf-8")



def Click(user_id, article_index):
    user_state = user_repre[user_id][0]
    con_state = user_repre[user_id][1]
    (user_state, con_state) = gru(art_encoded[article_index:article_index+1], con_state)
    user_repre[user_id] = (user_state, con_state)

class Recommender:
    def __init__(self):
        self.userID = ""
        self.readed = []
        pass
    def run(self):
        tk = Tk()
        tk.title("新闻推荐系统")
        self.login_frame = Frame()
        self.login_frame.pack(side = "top")
        self.login_entry = Entry(self.login_frame)
        self.login_entry.pack(side = "left", expand = True)
        self.login_button = Button(self.login_frame, text = "登录", command = self.confirm_userID)
        self.login_button.pack(side = "right", expand = True)
        self.rec_frame = Frame()
        self.rec_frame.pack(side = "bottom")
        tk.mainloop()
        pass
    def click_news(self, art_index):
        time_spot = time.clock()
        self.readed += [art_index,]
        output_file.write("\n\n%d\n"%art_index)
        Click(self.userID, art_index)
        output_file.write("time:%f" %(time.clock() - time_spot))
        self.refresh_news()
        output_file.write("time:%f" %(time.clock() - time_spot))
        pass
    def confirm_userID(self):
        self.userID = self.login_entry.get()
        if (self.userID != ""):
            if (self.userID not in user_repre):
                user_repre[self.userID] = (torch.zeros(1, HiddenDim), torch.zeros(1, ConDim))
            self.login_button["state"] = "disabled"
            self.login_entry["state"] = "disabled"
            self.add_news()
            self.refresh_news()
        pass
    def add_news(self):
        self.login_frame.destroy()
        self.news = []
        self.art_index = []
        for i in range(10):
            self.news += [Button(self.rec_frame, text = str(i)),]
            self.news[i].pack(side = "top")
            self.art_index += [0,]
        pass
        self.news[0].configure(command=self.click0)
        self.news[1].configure(command=self.click1)
        self.news[2].configure(command=self.click2)
        self.news[3].configure(command=self.click3)
        self.news[4].configure(command=self.click4)
        self.news[5].configure(command=self.click5)
        self.news[6].configure(command=self.click6)
        self.news[7].configure(command=self.click7)
        self.news[8].configure(command=self.click8)
        self.news[9].configure(command=self.click9)
        self.content_box = Text()
    def refresh_news(self):
        user_state = user_repre[self.userID][0]
        rec = Recommend(user_state[0, :], art_encoded, 10, set(self.readed))
        for i in range(10):
            art_index = rec[i]
            content = art_contents[art_index]
            if len(content) > 25:
                content = content[:25] + "..."
            self.news[i].configure(text = content, width= "40")
            self.art_index[i] = art_index
            output_file.write("%04d"%art_index + ":" + content)
            output_file.write("\n")
        output_file.write("\n")
        pass

    def click0(self):
        self.click_news(self.art_index[0])
    def click1(self):
        self.click_news(self.art_index[1])
    def click2(self):
        self.click_news(self.art_index[2])
    def click3(self):
        self.click_news(self.art_index[3])
    def click4(self):
        self.click_news(self.art_index[4])
    def click5(self):
        self.click_news(self.art_index[5])
    def click6(self):
        self.click_news(self.art_index[6])
    def click7(self):
        self.click_news(self.art_index[7])
    def click8(self):
        self.click_news(self.art_index[8])
    def click9(self):
        self.click_news(self.art_index[9])


def getRecommender(user_id):
    """
    为用户推荐时，只需计算单独一个用户即可；

    :param user_id:
    :return:
    """
    TrainRatio = 0.7
    reader_his, out_art_read = PreProcess_sql.PreprocessHistory(art_use_ids, 7000)
    # reader_his 中的元素： （user_id,[article_ids]）
    print("History Read.")
    reader_ids = [tuple[0] for tuple in reader_his]
    reader_record = [tuple[1] for tuple in reader_his]
    if user_id not in reader_ids:
        # 用户无操作记录，需要进行其他推荐方式 - 非个性化推荐
        return generate_recommender_list()
    gru = GRU(art_ids, reader_ids)  #
    gru.load(GRUSavePath + "7558.net")
    return gru.recommender_articles(art_encoded, user_id, reader_record, TrainRatio)


if __name__ == '__main__':
    # rec = Recommender()
    # rec.run()127385647 #
    user_id = 1008010
    print(getRecommender(user_id))
    print(getRecommender(25002630))
# History Read.
# [527, 1095, 566, 717, 722, 593, 910, 540, 924, 621]
# History Read.
# [1095, 566, 527, 722, 1001, 558, 593, 621, 540, 910]

# 25002630的浏览记录：<class 'list'>: [264, 264, 244, 244, 193, 193, 189, 188, 495, 502, 502]