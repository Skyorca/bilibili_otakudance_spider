import networkx as nx
import pandas as pd
import requests
import json
import global_var



up = pd.read_csv("up.csv")

def draw_otakudance_community(up):
    '''
    舞见关系网：如果A和B关系非常好，则A应该关注B，B也关注A，directed graph
    '''
    counter = 0
    mid_ = up.loc[:,"mid"]
    #up_name_ = up.loc[:,"up_name"]
    mid_list = []
    up_name = []
    up_num = len(mid_)
    for idx in range(up_num): #转换成两个很方便的列表表示
        mid_list.append(mid_[idx])
        #up_name.append(up_name_[idx])
    with open("up_community.txt","a+") as f:
        for mid in mid_list:
            following_list = []
            for page in range(1,6): 
                #b站限制看别人的关注只能看前五页pn，一页ps个，ps<=50，最大返回50*5=250following
                url = "https://api.bilibili.com/x/relation/followings?vmid={}&pn={}&ps=50&order=desc&jsonp=jsonp".format(mid,page)
                r = requests.get(url=url, headers=global_var.headers)
                following = json.loads(r.text)
                try:
                    following_ = following["data"]["list"] #是列表，每项是字典,可能轮空
                    for idx in range(len(following_)):
                        following_list.append(following_[idx]["mid"])
                except KeyError as err:
                    pass
            #以上构成了mid:[f1,f2,f3,...]这样一个mid-f1等的边关系，写入txt
            if len(following_list) != 0:
                for m in following_list:
                    if m in mid_list:
                        row = "{} {}\n".format(mid,m) #注意写入的是字符串信息
                        f.write(row)
            counter += 1
            if counter % 50 == 0: print("{}/{} is complited!!!".format(counter,up_num))
            #if counter % 50 == 0: break

draw_otakudance_community(up)



