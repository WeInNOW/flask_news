import json as js
from collections import Counter, OrderedDict
import numpy as np
from GeneralPara import *
# 直接没算时间戳，顺着向后排的

class Preprocess:
    # 输入：文章记录的路径
    # 输出：每个文章的ID、类别、内容，各成数组
    @staticmethod
    def PreprocessArticles(article_record, non_empty = False):

        if 'aaa'=='1':
            # 读记录并转换成数组
            art_ids = []
            art_cates = []
            art_contents = []
            art_timestamp = []
            with open(article_record, "r") as f:
                for line in f:
                    line_seg = line.split(":::")
                    attr = js.loads(line_seg[1])
                    id = int(line_seg[0])
                    cate = int(attr["categoryid"])
                    text = attr["text"]
                    timestamp = attr['timestamp']
                    if (not non_empty or len(text)>0):
                        art_ids += [id, ]
                        art_cates += [cate, ]
                        art_contents += [text, ]
                        art_timestamp +=[timestamp,]
            return art_ids, art_cates, art_contents,art_timestamp
        else:
            from preProcess_sql import PreProcess_sql
            return PreProcess_sql.PreprocessArticles()

    # 输入：文章的内容，停止词记录的路径
    # 输出：词例 每篇文章中的 所有可用词,是一个二维数组
    @staticmethod
    def Tokenize(art_contents, stopwords_txt):
        # Unicode下非ASCII的标点符号
        stop_punc_unicode = ["\u00ad", "\u00a0", "\u201c", "\u2026", "\u2013", "\u2122", "\u201e", "\u2014"]
        stop_words = set()
        # 读入停止词
        with open(stopwords_txt, "r") as swf:
            for word in swf:
                stop_words.add(word.replace("\n", ""))
        otoken_array = []
        for content in art_contents:  # 文章内容是所有文章的text数组，然后对每一篇文章而言
            for stop_punc in stop_punc_unicode:
                content.replace(stop_punc, " ")
            tokens = content.lower().split(" ")
            otokens = []
            for token in tokens:
                ostr = ""
                for ch in token:
                    if ch.isalpha():
                        ostr += ch
                if (len(ostr) and ostr not in stop_words):  # 去停用词
                    otokens += [ostr]
            otoken_array += [otokens, ]
        return otoken_array

    # 输入：词例
    # 输出：词频(array of map),最大词频(array)
    @staticmethod
    def CountToken(tokens_array, reserve_array=[]):
        """

        :param tokens_array: 二维数组，行表示文章，列表示文章中的单词
        :param reserve_array:
        :return:
        """
        max_freq_map = {}  # 所有单词在任意一篇文章中出现的最大频率
        token_count_array = []
        for tokens in tokens_array:  # 需要保持有序的
            for entry in Counter(tokens).items():
                token = entry[0]
                freq = entry[1]
                if token not in max_freq_map:
                    max_freq_map[token] = freq
                else:
                    max_freq_map[token] = max(freq, max_freq_map[token])
            # 字典转有序字典
            token_list = list(Counter(tokens))
            token_dict = dict(Counter(tokens))

            token_list.sort()
            token_item = OrderedDict()
            for key in token_list:
                token_item[key] = token_dict.get(key)

            token_count_array += [token_item, ]

        max_freq_array = list(max_freq_map.items())
        max_freq_array.sort(key=lambda tuple: (-tuple[1], tuple[0]))
        # 构造保留字数组，拼接到最大词频数组前，待用
        reserve_freq_array = []
        for token in reserve_array:
            reserve_freq = 1
            if token in max_freq_map:
                reserve_freq = max_freq_map[token]
            reserve_freq_array += [(token, reserve_freq), ]
        max_freq_array = reserve_freq_array + max_freq_array

        return token_count_array, max_freq_array
    #输入：词例
    #输出：词频(array of map),最大词频(array)
    @staticmethod
    def CountToken(tokens_array, reserve_array = []):
        max_freq_map = {} # 所有单词在任意一篇文章中出现的最大频率
        token_count_array = []
        for tokens in tokens_array:
            for entry in Counter(tokens).items():
                token = entry[0]
                freq = entry[1]
                if token not in max_freq_map:
                    max_freq_map[token] = freq
                else:
                    max_freq_map[token] = max(freq, max_freq_map[token])
            token_count_array += [dict(Counter(tokens)),]
        max_freq_array = list(max_freq_map.items())
        max_freq_array.sort(key = lambda tuple:-tuple[1])
        #构造保留字数组，拼接到最大词频数组前， 没有用到啊，构建的初衷是什么？
        reserve_freq_array = []
        for token in reserve_array:
            reserve_freq = 1
            if token in max_freq_map:
                reserve_freq = max_freq_map[token]
            reserve_freq_array += [(token, reserve_freq),]
        max_freq_array = reserve_freq_array + max_freq_array

        return token_count_array, max_freq_array
    #输入：词频(array of map)，最大词频(array)，以每个词出现的最高频率为分母，
    #输出：归一化词频：
    @staticmethod
    def Normalize(tokens_freqs, max_tokens_freqs, max_tokens = WordDim):
        '''

        :param tokens_freqs:
        :param max_tokens_freqs:
        :param max_tokens:
        :return:
        '''
        if (len(max_tokens_freqs) > max_tokens):
            max_tokens_freqs = max_tokens_freqs[:max_tokens] # 取出现频率最多的 wordDim维度的词语，只取4000维
        norm_tokens_freqs = []

        # max_tokens_freq_map=dict(max_tokens_freqs)

        max_tokens_freq_map = OrderedDict()# 这又是一个字典,再转为有序字典

        max_tokens_list = list(dict(max_tokens_freqs))
        max_tokens_list.sort()
        for max_token in max_tokens_list:
            max_tokens_freq_map[max_token] = dict(max_tokens_freqs).get(max_token)

        for tokens_map in tokens_freqs:
            norm_token = []

            for token_tuple in max_tokens_freqs:
                token = token_tuple[0]
                if token in tokens_map:
                    norm_freq = tokens_map[token] / max_tokens_freq_map[token]
                    norm_token += [norm_freq, ]
                else:
                    norm_token += [0.0, ]
            for i in range(max_tokens - len(max_tokens_freqs)):
                norm_token += [0.0,]
            norm_tokens_freqs += [norm_token,]  # 这里也没有保证每次相同
        return norm_tokens_freqs


    #输入：待取元素数组
    #输出：待取元素数目多于min_count的索引
    @staticmethod
    def MinCountClip(array, min_count = 0):
        return [i for i in range(len(array)) if len(array[i]) > min_count]
    #输入：读者阅读记录，文章ID
    #输出：[（读者ID，读者文章下标）],{article_id:[index,timestamp1,timestamp2 ...]}
    @staticmethod
    def PreprocessHistory(his_file, art_ids, min_time_seq = 5):
        art_id = np.asarray(art_ids)
        out_map = {}
        out_art_read = {}
        out_obj = []
        with open(his_file, "r") as f:
            for line in f:
                line_seg = line.split(":")
                userID = int(line_seg[0])
                readID = int(line_seg[1])
                timestamp = int(line_seg[2])
                unreadID = [int(s) for s in line_seg[8].split(",")]# 这里的一个误区是 其他系统的推荐信息
                if (len(unreadID)):
                    if len(np.where(art_id == readID)[0]): # art_id list中等于 readID的 一维下标
                        readInd = int(np.where(art_id == readID)[0][0]) # 取下标
                        unreadInd = [int(np.where(art_id == unid)[0][0]) for unid in unreadID if
                                     len(np.where(art_id == unid)[0]) > 0]
                        if len(unreadInd):
                            if (userID not in out_map):
                                out_map[userID] = []
                            out_map[userID] += [(timestamp, readInd, unreadInd)]
                #增加article_id : timestamp 的映射
                if readID not in out_art_read:
                    out_art_read[readID] = []
                    readIndx =np.where(art_id == readID)
                    if len(readIndx)< 1 or len(readIndx[0]) < 1:
                        readInd = -1
                    else:
                        readInd = readIndx[0][0]
                    out_art_read[readID].append(readInd)
                out_art_read[readID].append(timestamp)

        for userID in out_map.keys():

            if len(out_map[userID]) > min_time_seq:
                out_map[userID].sort(key=lambda x: x[0])  # 按时间戳排序
                out_obj += [(userID, [timeseq[1] for timeseq in out_map[userID]]),]
        return out_obj,out_art_read

