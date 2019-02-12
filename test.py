# -*- coding: <utf8> -*-
import requests
import re
from lxml import etree
import time
import html
import json
import global_var
from pyecharts import WordCloud
import jieba
from collections import Counter
import random

#####################################功能：个性化定制弹幕词云####################################################
def get_danmaku_content(cid):
    '''
    '''
    danmaku_url = "https://api.bilibili.com/x/v1/dm/list.so?oid={}".format(cid)
    r = requests.get(url = danmaku_url, headers = global_var.headers)
    #requests解析网页没有获取到该网页的编码格式，默认把编码格式设置为latin1（即 ISO-8859-1）了。可以理解为也就是进行了decode('latin1')操作,我们需要解回来也就是encode('latin1)
    tree = etree.HTML(r.text.encode('latin1'))  
    tree_ = tree.xpath("//d")
    content = []
    counter = 0
    for elem in tree_:
        if counter < 250:  #只拿500条弹幕信息
            c = elem.text
            content.append(c)
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
            
#调用这个函数，为up个性化定制弹幕词云
def draw_personalize_danmakucloud(up_name, aid_list):
    '''
    '''
    cid_list = []
    for av in aid_list:
        video_url = "https://api.bilibili.com/x/web-interface/view?aid={}".format(av)
        r = requests.get(url = video_url, headers = global_var.headers)
        video_info = json.loads(r.text) #r.text是一个json样式的字符串，转换成字典
        if video_info["message"] == '0': 
            cid = video_info['data']['cid']
            cid_list.append(cid)
    content = []
    for cid_ in cid_list:
        content += get_danmaku_content(cid_)
    draw_danmaku_cloud(content, up_name)

penta_aid = [41714571, 40360628,40117046,38850764,37370473,36011965,35107316,34943801,34827178,34371099,33449585,32054305,31678030,29575295,27514295,27337649,24811167,24162353,23158135,21563766,21379362,21035017,20481633,20375899,19779813,19780043,18931425,18564900,18412421]
aoye_aid  = [1987708,2728463,2476358,2349202,29458497,24623024,24303220,20812774,18775341,17736212,15970359,13415150,12019923,10929879,9193502,6774771,6235000,5845609]

#draw_personalize_danmakucloud("aoye",aoye_aid)

#####################################功能：广度填充####################################################


