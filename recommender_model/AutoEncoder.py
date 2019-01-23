import torch
import torch.nn as nn
import torch.nn.functional as fun
import torch.optim as optim
import pandas as pd
import numpy as np
from SeriModel import SeriModel
import matplotlib.pyplot as plot
from GeneralPara import *

BatchSize = 20
CorruptDim = 2000
MaxIter = 400
TripletWeight = 0.01
ShowLossGraph = False

def triplet_loss(anchor, positive, negative):
    log_like = torch.Tensor([0.0])
    for i in range(BatchSize):
        d_p = torch.mm(anchor[i:i+1, :], positive[i:i+1, :].transpose(0, 1))[0]
        d_n = torch.mm(anchor[i:i+1, :], negative[i:i+1, :].transpose(0, 1))[0]
        exp = torch.exp(torch.sub(d_n, d_p))
        log_like = torch.add(torch.log(torch.add(torch.Tensor([1.0,]), exp)), log_like)
    log_like = torch.div(log_like, torch.Tensor([BatchSize,]))
    return log_like

def PickTriplet(art_cat):
    same_cat_ind_dup = np.ndarray(1)
    while(same_cat_ind_dup.size <= 1):
        ind = torch.randperm(art_cat.size)[0]
        same_cat_ind_dup = np.where(art_cat == art_cat[ind])[0]
    same_cat_ind = same_cat_ind_dup[np.where(same_cat_ind_dup != ind)[0]]
    same_cat = same_cat_ind[torch.randperm(same_cat_ind.size)[0]]
    diff_cat_ind = np.where(art_cat != art_cat[ind])[0]
    diff_cat = diff_cat_ind[torch.randperm(diff_cat_ind.size)[0]]
    return [ind.item(), same_cat, diff_cat]

def PickBatch(token_freq, art_cat):
    triplet = np.ndarray((BatchSize, WordDim, 3))
    for i in range(BatchSize):
        triplet_ind = PickTriplet(art_cat)
        for j in range(3):
            triplet[i, :, j] = token_freq[triplet_ind[j]]
    return torch.Tensor(triplet)

class AutoEncoder(SeriModel):
    def __init__(self):
        super(AutoEncoder, self).__init__()
        self.input_size = WordDim
        self.hidden_size = HiddenDim
        self.win = nn.Linear(WordDim, HiddenDim)
        self.wout = nn.Linear(HiddenDim, WordDim)

    def encode(self, input):
        return torch.sub(torch.sigmoid(self.win(input)), torch.sigmoid(self.win.bias))

    def encodeNorm(self, input):
        return self.encode(torch.mul(input, torch.Tensor([1.0 - CorruptDim / WordDim])))

    def decode(self, hidden):
        return torch.sigmoid(self.wout(hidden))

    def forward(self, input):
        h = self.encode(input)
        return (h, self.decode(h))

    def trainModel(self, art_cat, word_freq, save_path):
        #optim mathod: RMS prop
        optimizer = optim.RMSprop(self.parameters(), lr=0.02)
        loss_list = []
        loss = torch.Tensor([0.0])
        for Iter in range(MaxIter):
            loss = torch.Tensor([0.0])
            self.zero_grad()
            target = PickBatch(word_freq, art_cat)
            input = target
            for j in range(3):
                for i in range(BatchSize):
                    input[i, torch.randperm(WordDim)[:CorruptDim], j] = 0.0
            output = []
            for i in range(3):
                output += [self(input[:, :, i]), ]
                loss = torch.add(torch.sum(torch.mul(output[i][1], target[:, :, i])), loss)
            loss = torch.div(loss, torch.Tensor([BatchSize]))
            t_loss = triplet_loss(output[0][0], output[1][0], output[2][0])
            loss = torch.add(torch.mul(t_loss, TripletWeight), loss)
            loss_list += [loss[0].item(),]
            #print("%.8f"% loss[0].item())
            loss.backward(retain_graph=True)
            optimizer.step()
        if (ShowLossGraph):
            plot.figure().gca().set_ylim(0.0, 0.2)
            plot.plot(range(len(loss_list)), loss_list)
            plot.show()
        print("AutoEncoder Train Loss:" + str(loss))
        self.save(save_path)
        # torch.save(self,save_path)
