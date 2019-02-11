from pyecharts import Pie,Bar,WordCloud
import pandas as pd
import re
import jieba
from collections import Counter
import wordcloud
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np

video = pd.read_csv("video.csv")
up    = pd.read_csv("up.csv")


def draw_sex_distrib(up):
    sex = up.loc[:,'sex'] #Series数据
    c1 = len(sex[sex=='男'])
    c2 = len(sex[sex=='女'])
    c3 = len(sex[sex=='保密'])
    x_ = ['男','女','保密']
    y_ = [c1,c2,c3]
    pie = Pie("B宅舞区：舞见男女比")
    pie.add("", x_, y_, is_label_show=True)
    pie.render("sex_distrib.html")


def draw_view_distrib(video):
    view = video.loc[:,'view']
    x_ = ["<500","500-1k","1k-5k","5k-1w","1w-3w","3w-5w","5w-10w","10w-20w","20w-50w","50w-100w",">100w"]
    num = [int(view[i]) for i in range(len(view))]
    c1= 0
    c2= 0
    c3= 0
    c4= 0
    c5= 0
    c6= 0
    c7= 0
    c8= 0
    c9= 0
    c10= 0
    c11= 0
    for elem in num:
        if elem<=500: c1 += 1
        elif elem>500 and elem<=1000: c2 += 1
        elif elem>1000 and elem<=5000: c3 += 1
        elif elem>5000 and elem<=10000: c4 += 1
        elif elem>10000 and elem<=30000: c5 += 1
        elif elem>30000 and elem<=50000: c6 += 1
        elif elem>50000 and elem<=100000: c7 += 1
        elif elem>100000 and elem<=200000: c8 += 1
        elif elem>200000 and elem<=500000: c9 += 1
        elif elem>500000 and elem<=1000000: c10 += 1
        else: c11 += 1
    y_ = [c1,c2,c3,c4,c5,c6,c7,c8,c9,c10,c11]
    bar = Bar("宅舞播放量分布")
    bar.add("播放量",x_, y_,xaxis_rotate=30)
    bar.render("view_distrib.html")

def draw_title_cloud(video):
    title_ = video.loc[:,"video_name"]
    title = str()
    for idx in range(len(title_)):
        title += title_[idx]
    #title = re.sub('【.*?】','',title)
    stopwords = {}.fromkeys([ line.rstrip() for line in open('stopwords.txt') ])
    segs = jieba.cut(title,cut_all=False)
    cloud_text =[]
    for seg in segs:
        if seg not in stopwords:
            cloud_text.append(seg)  
    fre= Counter(cloud_text)
    #print(fre)
    x_ = list(set(cloud_text))
    y_ = []
    assert(len(x_) == len(fre))
    for i in range(len(fre)):
        y_.append(fre[x_[i]])
    wordcloud = WordCloud(width=1300, height=620)
    wordcloud.add("宅舞标题词云", x_, y_, word_size_range=[20, 100])
    wordcloud.render("title_cloud.html")


draw_sex_distrib(up)
draw_view_distrib(video)
draw_title_cloud(video)
