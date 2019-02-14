import re

import jieba
import torch
import torch.nn as nn
import torch.optim as optim
import pandas as pd
import random as rand
import math,time
import json as js
import numpy as np
from Preprocess import Preprocess as Pre
import AutoEncoder as AE
from RNN import RNN,GRU,PickTest
from GeneralPara import *
from FilePathPara import *
from preProcess_sql import PreProcess_sql

def train_test_RNN_GRU(TrainAutoEncoder=False,TrainRNN = False,TestRNN = False,TrainGRU = False,TestGRU = True,TrainRatio=0.7,user_cnt = 7558):
    '''
    # rnn 真的梯度爆炸了~~，损失函数nan，
    :param TrainAutoEncoder:
    :param TrainRNN:
    :param TestRNN:
    :param TrainGRU:
    :param TestGRU:
    :param TrainRatio: 用户浏览历史做切分，训练集上的做直接的测试
    :return:
    '''
    # 预处理文章
    # art_ids, art_cats, art_contents,art_timestamp = Pre.PreprocessArticles(NewsDataSetPath)
    # art_ids, art_cats, art_contents, art_timestamp = PreProcess_sql.PreprocessArticles(user_cnt)
    art_ids, art_cats, raw_words, art_timestamp = PreProcess_sql.PreprocessArticles()
    art_contents = []  # 记录文章直接的切分词语，已去除了英文和数字
    for art_content in art_contents:
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
    print("News Read.")
    '''
    预处理文章完毕
    训练或加载AutoEncoder，并使用其编码文章
    这里编码文章，也需要不同规模？ - 有些文章没有出现在用户的点击行为到底需不需要,回头再看内容
    '''
    encoder = AE.AutoEncoder()

    if (TrainAutoEncoder):
        '''
        相同类别，与不同类别直接用category字段吗？
        '''
        encoder.trainModel(np.asarray(art_cats), torch.Tensor(art_norm_freq),
                           AutoEncoderSavePath + str(user_cnt) + ".net")
    else:
        encoder.load(AutoEncoderSavePath + str(user_cnt) + ".net")
        encoder.eval()
        encoder.train(False)

    middle_parameter = torch.Tensor(art_norm_freq)
    art_encoded = encoder.encodeNorm(middle_parameter)

    print("News Encoded.")
    # AutoEncoder完毕
    # 预处理浏览记录
    # reader_his,out_art_read = Pre.PreprocessHistory(HistoryDataSetPath, art_ids)
    reader_his, out_art_read = PreProcess_sql.PreprocessHistory(art_use_ids, user_cnt)
    print("History Read.")
    reader_ids = [tuple[0] for tuple in reader_his]
    reader_record = [tuple[1] for tuple in reader_his]
    #rand.Random(7).shuffle(reader_record) # 做了一次随机洗牌，结果不能重现 ~~ 洗牌需要对下标同时洗
    num_train_examples = math.floor(len(reader_his) * TrainRatio)
    print("History Preprocessed.")
    # RNN
    rnn = RNN(art_ids,reader_ids)
    if TrainRNN:
        print("RNN训练集loss:" + str(
            rnn.trainModel(art_encoded, reader_record, RNNSavePath + str(user_cnt) + ".net", TrainRatio)))
    if TestRNN:
        rnn.load(RNNSavePath + str(user_cnt) + ".net")

        print("RNN测试集准确率召回率：" + str(rnn.testModel(art_encoded, reader_record, TrainRatio)))
    # RNN完毕
    # GRU
    gru = GRU(art_ids,reader_ids)
    if TrainGRU:
        print("GRUTrainloss:" + str(
            gru.trainModel(art_encoded, reader_record, GRUSavePath + str(user_cnt) + ".net", TrainRatio)))
    else:
        gru.load(GRUSavePath + str(user_cnt) + ".net")  # 载入对应用户规模
        rnn.eval()
        rnn.train(False)
    if TestGRU:
        print("GRU测试准确率、召回率：" + str(gru.testModel(art_encoded, reader_record, TrainRatio)))
    # GRU完毕
    # 计算已有历史的读者状态
    user_repre = {}
    for i in range(len(reader_record)):
        input, readInd = PickTest(art_encoded, reader_record, i)
        hidden = gru.init_hidden()
        for j in range(input.shape[0]):
            output, hidden = gru(input[j:j + 1, :], hidden)
        user_state = []
        con_state = []
        for j in range(HiddenDim):
            user_state += [float(output[0, j]), ]
        for k in range(ConDim):
            con_state += [float(hidden[0, k]), ]
        user_repre[reader_ids[i]] = (user_state, con_state)
    js.dump(user_repre, open(UserStatePath, "w"), indent=2)  # 即便测试载入同样的模型，但所得user_state也并不相同
    print("User state computed")


def trains(user_cnt):
    train_test_RNN_GRU(TrainAutoEncoder=True, TrainRNN=False, TestRNN=False, TrainGRU=True,
                       TestGRU=True, user_cnt=user_cnt)


def tests(user_cnt):

    # TrainAutoEncoder = True,
    train_test_RNN_GRU(TestGRU=True,TrainRatio=0.7,user_cnt=user_cnt)


if __name__ == '__main__':

    # for i in range(1,8):
    #     print("user cnt(k):"+ str(i))
    #     trains(i*1000)
    trains(user_cnt=7558)
    # tests(1000)

