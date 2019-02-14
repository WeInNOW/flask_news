import torch
import torch.nn as nn
import torch.optim as optim
import pandas as pd
import numpy as np
import json as js
import json as js
import random as rand
import math
from SeriModel import SeriModel
import matplotlib.pyplot as plot
import threading as th
from GeneralPara import *

MaxIter = 3000
BatchSize = 20
TestRecommendCount = 10
DuplicateThresh = 40
RealtimeRecommend = False

SampleIndexList = []

def PickTrain(feature, his, train_ratio, ind = None):
    global SampleIndexList
    user = None
    if (len(SampleIndexList) == 0):
        SampleIndexList = torch.randperm(len(his))
    ind = SampleIndexList[0].item()
    SampleIndexList = SampleIndexList[1:]
    #select a user randomly
    user = his[ind]
    readInd = user[0:math.floor(len(user) * train_ratio)]
    readTensor = feature[readInd]
    unreadInd = []
    while len(unreadInd) < len(readInd):
        randomInd = torch.randperm(len(feature))[0].item()
        if randomInd not in set(user):
            unreadInd += [randomInd, ]
    unreadTensor = torch.stack([torch.Tensor(feature[unread]) for unread in unreadInd])
    return torch.Tensor(readTensor[:-1, :]), torch.Tensor(readTensor[1:, :]), unreadTensor[1:]

def PickTest(feature, his, ind):
    user = his[ind]
    readInd = user
    readTensor = feature[readInd]
    return torch.Tensor(readTensor[:-1, :]), readInd[1:]

def RecommendTest(user_state, feature, num_rec):
    list = [(i, float(torch.dot(torch.Tensor(feature[i, :]), user_state))) for i in range(feature.shape[0])]
    list.sort(key=lambda x: -x[1])
    list = [item[0] for item in list]
    return list[:num_rec]

def Recommend(user_state, feature, num_rec, set_to_ignore = set()):
    list = [(i, float(torch.dot(torch.Tensor(feature[i, :]), user_state))) for i in range(feature.shape[0])]
    list.sort(key=lambda x:-x[1])
    list = [item[0] for item in list]
    list = Deduplicate(list, feature, num_rec, set_to_ignore)
    return list[:num_rec]

def Deduplicate(rec_list, feature, num_rec, set_to_ignore):
    res = []
    for i in rec_list:
        dup = False
        for j in res:
            if float(torch.dot(torch.Tensor(feature[i, :]), torch.Tensor(feature[j, :]))) > DuplicateThresh:
                dup = True
        if not dup and i not in set_to_ignore:
            res += [i, ]
        if len(res) >= num_rec:
            break
    return res

def Plot(x, y, name):
    thread = th.Thread(target = PlotThread, args = (x, y, name))
    thread.daemon = True
    thread.start()

def PlotThread(x, y, name):
    fig = plot.figure()
    fig.canvas.set_window_title(name)
    axis = fig.gca()
    axis.set_ylim(0.0, 1.0)
    plot.plot(x, y)
    plot.show()
# input: timestep x feature
# positive: same as input
# negative: same as input
# output: loss tensor
def SeqLoss(input, positive, negative, num_exa = None):
    if (num_exa == None):
        num_exa = input.shape[0]
    diff = torch.sub(torch.sum(torch.mul(input, positive)), torch.sum(torch.mul(input, negative)))
    sig = torch.clamp(torch.sigmoid(diff), 0.00000001, 0.9999999)
    log_dis = torch.log(sig)
    loss = torch.div(torch.mul(log_dis, torch.Tensor([-1.0])), torch.Tensor([float(num_exa)]))
    return loss

class RNN(SeriModel):
    def __init__(self, art_ids, reader_ids):
        hidden_size = HiddenDim
        super(RNN, self).__init__()
        self.hidden_size = hidden_size
        self.w = nn.Linear(hidden_size + hidden_size, hidden_size)
        self.name = "RNN"
        self.art_ids = art_ids
        self.reader_ids = reader_ids
    #正向传播
    def forward(self, input, hidden):
        input_combined = torch.cat((input, hidden), 1)
        output = self.w(input_combined)
        return output, output
    def init_hidden(self):
        return torch.zeros(1, self.hidden_size)

    #输出：最后的loss值
    def trainModel(self, feature, user_his, save_path, train_ratio):
        optimizer = optim.RMSprop(self.parameters(), lr=0.02)
        loss_list = []
        for iter in range(MaxIter):
            time_seq_loss = 0
            optimizer.zero_grad()
            loss = torch.Tensor([0.0, ])
            for batch in range(BatchSize):
                input, positive, negative = PickTrain(feature, user_his, train_ratio)
                hidden = self.init_hidden()
                for i in range(input.shape[0]):
                    output, hidden = self(input[i:i + 1, :], hidden)
                    loss = torch.add(SeqLoss(output, positive[i:i + 1, :], negative[i:i + 1, :], input.shape[0]), loss)
            loss = torch.div(loss, torch.Tensor([BatchSize]))
            loss.backward(retain_graph=True)
            nn.utils.clip_grad_value_(self.parameters(), 10000)
            loss_list += [loss[0].item(), ]

            #print("%04d"% len(loss_list) + ":%.6f"% loss[0].item())

            optimizer.step()
        self.save(save_path)
        # Plot(range(len(loss_list)), loss_list, self.name)  #
        return loss_list[-1]

    #输出：准确率、召回率
    def testModel(self, feature, user_his, train_ratio):
        '''
        推荐策略是什么，一次推荐10个，只要其中有一个命中，就hit + 1 ，总数 + 10  - 这是实时推荐
        但是离线推荐并不是这样，推荐10个，看总共有多少个命中

        是train_ratio的作为测试
        :param feature:
        :param user_his:
        :param train_ratio:
        :return:
        '''
        self.train(False)
        num_hit = 0
        num_positive = 0
        num_test = 0
        for i in range(len(user_his)):
            input, readInd = PickTest(feature, user_his, i)  # 现场训练
            hidden = self.init_hidden()
            output = None
            for j in range(math.floor(input.shape[0] * train_ratio)):
                output, hidden = self(input[j:j + 1, :], hidden)
            if (RealtimeRecommend):# 实时推荐
                for j in range(math.floor(input.shape[0] * train_ratio), input.shape[0]):
                    output, hidden = self(input[j:j + 1, :], hidden)
                    num_positive += 1
                    num_test += TestRecommendCount
                    user_state = output[0, :]
                    read_ind = readInd[j]
                    recommend_set = RecommendTest(user_state, feature, TestRecommendCount)
                    if read_ind in recommend_set:
                        num_hit += 1
            else:
                user_state = output[0, :]
                recommend_set = RecommendTest(user_state, feature, TestRecommendCount)
                num_test += TestRecommendCount
                for j in range(math.floor(input.shape[0] * train_ratio), input.shape[0]): # 对用户的行为做竖向切割
                    num_positive += 1
                    read_ind = readInd[j]
                    if read_ind in recommend_set:
                        num_hit += 1
        return num_hit/(num_test), num_hit/num_positive

    #获取推荐列表
    def recommender_articles(self, feature, user_id, user_his, train_ratio):

        self.train(False)
        num_hit = 0
        num_positive = 0
        num_test = 0
        # 获取用户user_id对应的下标
        i = self.reader_ids.index(user_id)  # 127385647 , 10387504
        input, readInd = PickTest(feature, user_his, i)  # 现场训练, 有模型了
        hidden = self.init_hidden()
        output = None
        for j in range(math.floor(input.shape[0] * train_ratio)):
            output, hidden = self(input[j:j + 1, :], hidden)
        if (RealtimeRecommend):# 实时推荐
            for j in range(math.floor(input.shape[0] * train_ratio), input.shape[0]):
                output, hidden = self(input[j:j + 1, :], hidden)
                num_positive += 1
                num_test += TestRecommendCount
                user_state = output[0, :]
                read_ind = readInd[j]
                recommend_set = RecommendTest(user_state, feature, TestRecommendCount)
        else:
            user_state = output[0, :]
            recommend_set = RecommendTest(user_state, feature, TestRecommendCount)

        return [self.art_ids[index] for index in recommend_set]
        # return recommend_set


class GRU(RNN):
    def __init__(self, art_ids, reader_ids):
        super(GRU, self).__init__(art_ids, reader_ids)
        input_size = HiddenDim
        control_size = ConDim
        self.input_size = input_size
        self.control_size = control_size
        self.wz = nn.Linear(input_size + control_size, control_size)
        self.wr = nn.Linear(input_size + control_size, control_size)
        self.we = nn.Linear(input_size + control_size, control_size)
        self.wd = nn.Linear(control_size, input_size)
        self.name = "GRU"

    def forward(self, input, hidden):
        input_combined = torch.cat((input, hidden), 1)
        gz = torch.sigmoid(self.wz(input_combined))
        gr = torch.sigmoid(self.wr(input_combined))
        enc = torch.tanh(self.we(torch.cat((input, torch.mul(gr, hidden)), 1)))
        h = torch.add(torch.mul(gz, enc), torch.mul(torch.sub(torch.Tensor([1.0]), gz), hidden))
        dec = torch.tanh(self.wd(h))
        return dec, h

    def init_hidden(self):
        return torch.zeros(1, self.control_size)
