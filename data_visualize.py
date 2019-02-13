from pyecharts import Pie,Bar,Line,WordCloud,ThemeRiver
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
import json

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
    只拿一个视频的弹幕信息，返回字符串
    '''
    danmaku_url = "https://api.bilibili.com/x/v1/dm/list.so?oid={}".format(cid)
    r = requests.get(url = danmaku_url, headers = global_var.headers)
    #requests解析网页没有获取到该网页的编码格式,默认把编码格式设置为latin1（即 ISO-8859-1）了。可以理解为也就是进行了decode('latin1')操作,我们需要解回来也就是encode('latin1)
    tree = etree.HTML(r.text.encode('latin1'))  
    tree_ = tree.xpath("//d")
    content = str()
    counter = 0
    for elem in tree_:
        if counter < 500:  #只拿500条弹幕信息
            c = elem.text
            content += c
            counter += 1
        else: break
    return content


def draw_danmaku_cloud(content, name=''):
    '''
    content: 整合一个或者多个视频的弹幕信息的字符串
    '''
    stopwords = {}.fromkeys([ line.rstrip() for line in open('stopwords.txt') ])
    segs = jieba.cut(content, cut_all=False)
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
    wordcloud.add("风气鉴定w", x_, y_, word_size_range=[20, 200])
    wordcloud.render("{}_danmaku_cloud.html".format(name))


def draw_yearly_danmaku_keyword_cloud(video):
    '''
    画年度弹幕关键词变化图
    '''
    video_cid  = video.loc[:,'cid']
    video_time = video.loc[:,'pubtime']  #这里取出来的是形如2010/5/21 23:40的字符串,要转换成时间戳
    video_time_ = []
    for i in range(len(video_time)):
        if pd.isnull(video_time[i]) or video_time[i] == '1': video_time_.append(0)  #之后时间为0的跳过就行了,简单粗暴
        else: video_time_.append(int(time.mktime(time.strptime('{}'.format(video_time[i]), '%Y/%m/%d %H:%M'))))
    assert(len(video_time) == len(video_time_))
    ###年份的时间戳###
    yr2009 = 1230739200  #表示2009开始，下同
    yr2009_ = 1262275199 #表示2009结束，下同
    yr2010 = 1262275200
    yr2010_ = 1293811199
    yr2011 = 1293811200  
    yr2011_ = 1325347199 
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
    ###定制关键词列表
    tui = []
    xiong = []
    siwa = []
    yeman = []
    boy = []
    year_list = [yr2009,yr2009_,yr2010,yr2010_,yr2011,yr2011_,yr2012,yr2012_,yr2013,yr2013_,yr2014,yr2014_,yr2015,yr2015_,yr2016,yr2016_,yr2017,yr2017_,yr2018,yr2018_]
    for yr in range(0,19,2):
        in_this_year = []  #在此年的下标数组
        for idx in range(len(video_time_)):  
            if video_time_[idx]>=year_list[yr] and video_time_[idx]<=year_list[yr+1]: in_this_year.append(idx)
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
        yeman.append(content.count("撸")+content.count("完事")+content.count("好了")+content.count("Pr")+content.count("pr")+content.count("舔")+content.count("射"))
        boy.append(content.count("男")+content.count("小哥哥")+content.count("汉子"))
        print('{} done!'.format(yr))
    x_ = ['2009','2010','2011','2012','2013','2014','2015','2016','2017','2018']
    bar = Bar("舞区风气关键词年度变化图")
    bar.use_theme("macarons")
    bar.add("腿",x_,tui)
    bar.add("胸",x_,xiong)
    bar.add("袜",x_,siwa)
    bar.add("绅士行为",x_,yeman)
    bar.render("风气年度变化图.html")
    bar_ = Bar("男孩子")
    bar_.add("男孩子",x_,boy)
    bar_.render("男孩子.html")
    



def draw_monthly_danmaku_keyword_cloud(video):
    '''
    弹幕中的某个关键词随月份变化的河流图
    '''
    video_cid  = video.loc[:,'cid']
    video_time = video.loc[:,'pubtime']  #这里取出来的是形如2010/5/21 23:40的字符串,要转换成时间戳
    video_time_ = []
    for i in range(len(video_time)):
        if pd.isnull(video_time[i]) or video_time[i] == '1': video_time_.append(0)  #之后时间为0的跳过就行了,简单粗暴
        else: video_time_.append(int(time.mktime(time.strptime('{}'.format(video_time[i]), '%Y/%m/%d %H:%M'))))
    assert(len(video_time) == len(video_time_))
    ###寻找每个月的起止时间戳,这是2018年的###
    mn1 = 1514736000
    mn1_ = 1517414399
    mn2 = 1517414400
    mn2_ = 1519833599
    mn3 = 1519833600
    mn3_ = 1522511999
    mn4 = 1522512000
    mn4_ = 1525103999
    mn5 = 1525104000
    mn5_ = 1527782399
    mn6 = 1527782400
    mn6_ = 1530374399
    mn7 = 1530374400
    mn7_ = 1533052799
    mn8 = 1533052800
    mn8_ = 1535731199
    mn9 = 1535731200
    mn9_ = 1538323199
    mn10 = 1538323200
    mn10_ = 1541001599
    mn11 = 1541001600
    mn11_ = 1543593599
    mn12 = 1543593600
    mn12_ = 1546271999
    ###在这里定制你的key-word列表###
    tui = []
    xiong = []
    siwa = []
    yeman = []
    ###月份列表###
    month_list = [mn1,mn1_,mn2,mn2_,mn3,mn3_,mn4,mn4_,mn5,mn5_,mn6,mn6_,mn7,mn7_,mn8,mn8_,mn9,mn9_,mn10,mn10_,mn11,mn11_,mn12,mn12_]
    for mnth in range(0,23,2):
        in_this_month = []
        for idx in range(len(video_time_)):  
            if video_time_[idx]>=month_list[mnth] and video_time_[idx]<=month_list[mnth+1]: in_this_month.append(idx)
        random.shuffle(in_this_month)
        content = str()
        counter = 0
        for idx in in_this_month:
            if counter > 1000: break #每月只拿1000个稿件的弹幕
            cid = video_cid[idx]
            c   = get_danmaku_content(cid)
            content += c
            counter += 1
        tui.append(content.count("腿"))
        xiong.append(content.count("胸")+content.count("奶")+content.count("乳"))
        siwa.append(content.count("黑丝")+content.count("白丝"))
        yeman.append(content.count("撸")+content.count("完事")+content.count("好了")+content.count("Pr")+content.count("pr")+content.count("舔")+content.count("射"))
        print('{} done'.format(mnth))
    data = [
        ['2018/01/01',tui[0],"腿"],['2018/02/01',tui[1],"腿"],['2018/03/01',tui[2],"腿"],['2018/04/01',tui[3],"腿"],
        ['2018/05/01',tui[4],"腿"],['2018/06/01',tui[5],"腿"],['2018/07/01',tui[6],"腿"],['2018/08/01',tui[7],"腿"],
        ['2018/09/01',tui[8],"腿"],['2018/10/01',tui[9],"腿"],['2018/11/01',tui[10],"腿"],['2018/12/01',tui[11],"腿"],
        ['2018/01/01',xiong[0],"胸"],['2018/02/01',xiong[1],"胸"],['2018/03/01',xiong[2],"胸"],['2018/04/01',xiong[3],"胸"],
        ['2018/05/01',xiong[4],"胸"],['2018/06/01',xiong[5],"胸"],['2018/07/01',xiong[6],"胸"],['2018/08/01',xiong[7],"胸"],
        ['2018/09/01',xiong[8],"胸"],['2018/10/01',xiong[9],"胸"],['2018/11/01',xiong[10],"胸"],['2018/12/01',xiong[11],"胸"],
        ['2018/01/01',siwa[0],"袜"],['2018/02/01',siwa[1],"袜"],['2018/03/01',siwa[2],"袜"],['2018/04/01',siwa[3],"袜"],
        ['2018/05/01',siwa[4],"袜"],['2018/06/01',siwa[5],"袜"],['2018/07/01',siwa[6],"袜"],['2018/08/01',siwa[7],"袜"],
        ['2018/09/01',siwa[8],"袜"],['2018/10/01',siwa[9],"袜"],['2018/11/01',siwa[10],"袜"],['2018/12/01',siwa[11],"袜"],
        ['2018/01/01',yeman[0],"绅士"],['2018/02/01',yeman[1],"绅士"],['2018/03/01',yeman[2],"绅士"],['2018/04/01',yeman[3],"绅士"],
        ['2018/05/01',yeman[4],"绅士"],['2018/06/01',yeman[5],"绅士"],['2018/07/01',yeman[6],"绅士"],['2018/08/01',yeman[7],"绅士"],
        ['2018/09/01',yeman[8],"绅士"],['2018/10/01',yeman[9],"绅士"],['2018/11/01',yeman[10],"绅士"],['2018/12/01',yeman[11],"绅士"]
        ]
    tr = ThemeRiver("宅舞卖rou__弹幕统计河流图")
    tr.add(["胸","腿","袜","绅士"],data,is_label_show=True)
    tr.render("舞区卖肉__弹幕统计河流图.html")



def draw_post_yearly_change(video):
    '''
    '''
    video_time = video.loc[:,'pubtime']  #这里取出来的是形如2010/5/21 23:40的字符串,要转换成时间戳
    video_time_ = []
    for i in range(len(video_time)):
        if pd.isnull(video_time[i]) or video_time[i] == '1': video_time_.append(0)  #之后时间为0的跳过就行了,简单粗暴
        else: video_time_.append(int(time.mktime(time.strptime('{}'.format(video_time[i]), '%Y/%m/%d %H:%M'))))
    assert(len(video_time) == len(video_time_))
    ###年份的时间戳###
    yr2009 = 1230739200  #表示2009开始，下同
    yr2009_ = 1262275199 #表示2009结束，下同
    yr2010 = 1262275200
    yr2010_ = 1293811199
    yr2011 = 1293811200  
    yr2011_ = 1325347199 
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
    c1 = 0
    c2 = 0
    c3 = 0
    c4 = 0
    c5 = 0
    c6 = 0
    c7 = 0
    c8 = 0
    c9 = 0
    c10 = 0
    for idx in range(len(video_time_)):
        if video_time_[idx] >= yr2009 and video_time_[idx]<=yr2009_ and video_time_[idx] != 0: c1 += 1
        elif video_time_[idx] >= yr2010 and video_time_[idx]<=yr2010_: c2 += 1
        elif video_time_[idx] >= yr2011 and video_time_[idx]<=yr2011_: c3 += 1
        elif video_time_[idx] >= yr2012 and video_time_[idx]<=yr2012_: c4 += 1
        elif video_time_[idx] >= yr2013 and video_time_[idx]<=yr2013_: c5 += 1
        elif video_time_[idx] >= yr2014 and video_time_[idx]<=yr2014_: c6 += 1
        elif video_time_[idx] >= yr2015 and video_time_[idx]<=yr2015_: c7 += 1
        elif video_time_[idx] >= yr2016 and video_time_[idx]<=yr2016_: c8 += 1
        elif video_time_[idx] >= yr2017 and video_time_[idx]<=yr2017_: c9 += 1
        elif video_time_[idx] >= yr2018 and video_time_[idx]<=yr2018_: c10 += 1
    x_ = ['2009','2010','2011','2012','2013','2014','2015','2016','2017','2018']
    post = [c1,c2,c3,c4,c5,c6,c7,c8,c9,c10]
    print(post)
    bar = Bar("宅舞区十年投稿数量变化")
    bar.add("投稿数",x_,post,xaxis_rotate=30)
    bar.render("十年投稿数量变化.html")


def draw_maitui_danmaku_cloud():
    '''
    画那些卖腿的up主的弹幕词云
    '''
    ###自己在maitui_list填入卖腿up的作品av号###
    maitui_list = []
    cid_list = []
    content = str()
    for v in maitui_list:
        video_url = "https://api.bilibili.com/x/web-interface/view?aid={}".format(v)
        r = requests.get(url = video_url, headers = global_var.headers)
        video_info = json.loads(r.text) #r.text是一个json样式的字符串，转换成字典
        cid_list.append(video_info['data']['cid'])
    for cid in cid_list:
        content_ = get_danmaku_content(cid)
        content += content_
    draw_danmaku_cloud(content,"卖腿")


#draw_sex_distrib(up)
#draw_view_distrib(video)
#draw_title_cloud(video)
#draw_post_yearly_change(video)
#draw_monthly_danmaku_keyword_cloud(video)
#draw_yearly_danmaku_keyword_cloud(video)
#draw_maitui_danmaku_cloud()
