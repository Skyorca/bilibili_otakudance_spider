from pyecharts import Pie,Bar,Line,WordCloud
import pandas as pd
import re
import jieba
from collections import Counter
import numpy as np
import time
import random
from lxml import etree
import requests
import global_var

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


def get_danmaku_content(cid):
    '''
    '''
    danmaku_url = "https://api.bilibili.com/x/v1/dm/list.so?oid={}".format(cid)
    r = requests.get(url = danmaku_url, headers = global_var.headers)
    #requests解析网页没有获取到该网页的编码格式，默认把编码格式设置为latin1（即 ISO-8859-1）了。可以理解为也就是进行了decode('latin1')操作,我们需要解回来也就是encode('latin1)
    tree = etree.HTML(r.text.encode('latin1'))  
    tree_ = tree.xpath("//d")
    content = str()
    counter = 0
    for elem in tree_:
        if counter < 250:  #只拿500条弹幕信息
            c = elem.text
            content += c
            counter += 1
        else: break
    return content


def draw_danmaku_cloud(content, name=''):
    '''
    '''
    danmaku = str()
    for c in content:
        danmaku += c
    stopwords = {}.fromkeys([ line.rstrip() for line in open('stopwords.txt') ])
    segs = jieba.cut(danmaku, cut_all=False)
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
    wordcloud.add("宅舞弹幕词云", x_, y_, word_size_range=[20, 200])
    wordcloud.render("{}_danmaku_cloud.html".format(name))


def draw_yearly_danmaku_cloud(video):
    '''
    '''
    video_cid  = video.loc[:,'cid']
    video_time = video.loc[:,'pubtime']  #这里取出来的是形如2010/5/21 23:40的字符串，要转换成时间戳
    video_time_ = []
    for i in range(len(video_time)):
        if pd.isnull(video_time[i]) or video_time[i] == '1': video_time_.append(0)  #之后时间为0的跳过就行了，简单粗暴
        else: video_time_.append(int(time.mktime(time.strptime('{}'.format(video_time[i]), '%Y/%m/%d %H:%M'))))
    assert(len(video_time) == len(video_time_))
    yr2009 = 1230739200
    yr2009_ = 1262275199
    yr2010 = 1262275200
    yr2010_ = 1293811199
    yr2011 = 1293811200  #表示2011年开始
    yr2011_ = 1325347199 #表示2011年结束，下同
    yr2012 = 1325347200
    yr2012_ = 1356969599
    yr2013 = 1356969600
    yr2013_ = 1388505599
    yr2014 = 1388505600
    yr2014_ = 1420041599
    yr2015 = 1420041600
    yr2015_ = 1451577599
    yr2016 = 1451577600
    yr2016_ = 1483199999
    yr2017 = 1483200000
    yr2017_ = 1514735999
    yr2018 = 1514736000
    yr2018_ = 1546271999

    tui = []
    xiong = []
    siwa = []
    yeman = []

    in_this_year = []  #在此年的下标数组
    for idx in range(len(video_time_)):  
        if video_time_[idx]>=yr2009 and video_time_[idx]<=yr2009_: in_this_year.append(idx)
    random.shuffle(in_this_year)
    content = str()
    counter = 0
    for idx in in_this_year:
        if counter > 500: break #每年只拿500个稿件的弹幕
        cid = video_cid[idx]
        c   = get_danmaku_content(cid)
        content += c
        counter += 1
    tui.append(content.count("腿"))
    xiong.append(content.count("胸")+content.count("奶")+content.count("乳"))
    siwa.append(content.count("黑丝")+content.count("白丝"))
    yeman.append(content.count("撸")+content.count("完事")+content.count("好了")+content.count("Pr")+content.count("pr"))

    in_this_year = []  #在此年的下标数组
    for idx in range(len(video_time_)):  
        if video_time_[idx]>=yr2010 and video_time_[idx]<=yr2010_: in_this_year.append(idx)
    random.shuffle(in_this_year)
    content = str()
    counter = 0
    for idx in in_this_year:
        if counter > 500: break #每年只拿500个稿件的弹幕
        cid = video_cid[idx]
        c   = get_danmaku_content(cid)
        content += c
        counter += 1
    tui.append(content.count("腿"))
    xiong.append(content.count("胸")+content.count("奶")+content.count("乳"))
    siwa.append(content.count("黑丝")+content.count("白丝"))
    yeman.append(content.count("撸")+content.count("完事")+content.count("好了")+content.count("Pr")+content.count("pr"))
    
    #draw_danmaku_cloud(content,'2016')

    in_this_year = []  #在此年的下标数组
    for idx in range(len(video_time_)):  
        if video_time_[idx]>=yr2011 and video_time_[idx]<=yr2011_: in_this_year.append(idx)
    random.shuffle(in_this_year)
    content = str()
    counter = 0
    for idx in in_this_year:
        if counter > 500: break #每年只拿500个稿件的弹幕
        cid = video_cid[idx]
        c   = get_danmaku_content(cid)
        content += c
        counter += 1
    tui.append(content.count("腿"))
    xiong.append(content.count("胸")+content.count("奶")+content.count("乳"))
    siwa.append(content.count("黑丝")+content.count("白丝"))
    yeman.append(content.count("撸")+content.count("完事")+content.count("好了")+content.count("Pr")+content.count("pr"))

    in_this_year = []  #在此年的下标数组
    for idx in range(len(video_time_)):  
        if video_time_[idx]>=yr2012 and video_time_[idx]<=yr2012_: in_this_year.append(idx)
    random.shuffle(in_this_year)
    content = str()
    counter = 0
    for idx in in_this_year:
        if counter > 500: break #每年只拿500个稿件的弹幕
        cid = video_cid[idx]
        c   = get_danmaku_content(cid)
        content += c
        counter += 1
    tui.append(content.count("腿"))
    xiong.append(content.count("胸")+content.count("奶")+content.count("乳"))
    siwa.append(content.count("黑丝")+content.count("白丝"))
    yeman.append(content.count("撸")+content.count("完事")+content.count("好了")+content.count("Pr")+content.count("pr"))

    in_this_year = []  #在此年的下标数组
    for idx in range(len(video_time_)):  
        if video_time_[idx]>=yr2013 and video_time_[idx]<=yr2013_: in_this_year.append(idx)
    random.shuffle(in_this_year)
    content = str()
    counter = 0
    for idx in in_this_year:
        if counter > 500: break #每年只拿500个稿件的弹幕
        cid = video_cid[idx]
        c   = get_danmaku_content(cid)
        content += c
        counter += 1
    tui.append(content.count("腿"))
    xiong.append(content.count("胸")+content.count("奶")+content.count("乳"))
    siwa.append(content.count("黑丝")+content.count("白丝"))
    yeman.append(content.count("撸")+content.count("完事")+content.count("好了")+content.count("Pr")+content.count("pr"))

    in_this_year = []  #在此年的下标数组
    for idx in range(len(video_time_)):  
        if video_time_[idx]>=yr2014 and video_time_[idx]<=yr2014_: in_this_year.append(idx)
    random.shuffle(in_this_year)
    content = str()
    counter = 0
    for idx in in_this_year:
        if counter > 500: break #每年只拿500个稿件的弹幕
        cid = video_cid[idx]
        c   = get_danmaku_content(cid)
        content += c
        counter += 1
    tui.append(content.count("腿"))
    xiong.append(content.count("胸")+content.count("奶")+content.count("乳"))
    siwa.append(content.count("黑丝")+content.count("白丝"))
    yeman.append(content.count("撸")+content.count("完事")+content.count("好了")+content.count("Pr")+content.count("pr"))

    in_this_year = []  #在此年的下标数组
    for idx in range(len(video_time_)):  
        if video_time_[idx]>=yr2015 and video_time_[idx]<=yr2015_: in_this_year.append(idx)
    random.shuffle(in_this_year)
    content = str()
    counter = 0
    for idx in in_this_year:
        if counter > 500: break #每年只拿500个稿件的弹幕
        cid = video_cid[idx]
        c   = get_danmaku_content(cid)
        content += c
        counter += 1
    tui.append(content.count("腿"))
    xiong.append(content.count("胸")+content.count("奶")+content.count("乳"))
    siwa.append(content.count("黑丝")+content.count("白丝"))
    yeman.append(content.count("撸")+content.count("完事")+content.count("好了")+content.count("Pr")+content.count("pr"))

    in_this_year = []  #在此年的下标数组
    for idx in range(len(video_time_)):  
        if video_time_[idx]>=yr2016 and video_time_[idx]<=yr2016_: in_this_year.append(idx)
    random.shuffle(in_this_year)
    content = str()
    counter = 0
    for idx in in_this_year:
        if counter > 500: break #每年只拿500个稿件的弹幕
        cid = video_cid[idx]
        c   = get_danmaku_content(cid)
        content += c
        counter += 1
    tui.append(content.count("腿"))
    xiong.append(content.count("胸")+content.count("奶")+content.count("乳"))
    siwa.append(content.count("黑丝")+content.count("白丝"))
    yeman.append(content.count("撸")+content.count("完事")+content.count("好了")+content.count("Pr")+content.count("pr"))

    in_this_year = []  #在此年的下标数组
    for idx in range(len(video_time_)):  
        if video_time_[idx]>=yr2017 and video_time_[idx]<=yr2017_: in_this_year.append(idx)
    random.shuffle(in_this_year)
    content = str()
    counter = 0
    for idx in in_this_year:
        if counter > 500: break #每年只拿500个稿件的弹幕
        cid = video_cid[idx]
        c   = get_danmaku_content(cid)
        content += c
        counter += 1
    tui.append(content.count("腿"))
    xiong.append(content.count("胸")+content.count("奶")+content.count("乳"))
    siwa.append(content.count("黑丝")+content.count("白丝"))
    yeman.append(content.count("撸")+content.count("完事")+content.count("好了")+content.count("Pr")+content.count("pr"))

    in_this_year = []  #在此年的下标数组
    for idx in range(len(video_time_)):  
        if video_time_[idx]>=yr2018 and video_time_[idx]<=yr2018_: in_this_year.append(idx)
    random.shuffle(in_this_year)
    content = str()
    counter = 0
    for idx in in_this_year:
        if counter > 500: break #每年只拿500个稿件的弹幕
        cid = video_cid[idx]
        c   = get_danmaku_content(cid)
        content += c
        counter += 1
    tui.append(content.count("腿"))
    xiong.append(content.count("胸")+content.count("奶")+content.count("乳"))
    siwa.append(content.count("黑丝")+content.count("白丝"))
    yeman.append(content.count("撸")+content.count("完事")+content.count("好了")+content.count("Pr")+content.count("pr"))

    return(tui, xiong, siwa, yeman)
'''
def draw_keyword_time_change(hentai_result):
    #我的Line折线图有问题，画不出来
    tui = hentai_result[0]
    xiong = hentai_result[1]
    siwa = hentai_result[2]
    yeman = hentai_result[3]
    x_ = [2009,2010,2011,2012,2013,2014,2015,2016,2017,2018]
    line = Line("舞区卖肉趋势曲线") 
    line.add("腿",x_,tui, is_smooth=True)
    line.add("胸",x_,xiong, is_smooth=True)
    line.add("丝袜",x_,siwa, is_smooth=True)
    line.add("绅士行为",x_,yeman, is_smooth=True)
    line.render()
'''

    
    
#hentai_result = draw_yearly_danmaku_cloud(video)
draw_keyword_time_change()


























'''
draw_sex_distrib(up)
draw_view_distrib(video)
draw_title_cloud(video)
'''