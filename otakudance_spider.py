import requests
import re
from lxml import etree
import time
import html
import json
import global_var
from mysql_manager import MySQLManager
class OtakuDanceSpider:

        def __init__(self):
            self.mysql_manager = MySQLManager(global_var.crawer_thread) #单线程爬虫

        video_count = 0

        def get_hot_tag(self):
                '''
                舞区的热门标签整理列表,写入hottag.txt 
                '''
                url_otaku_dance = requests.get("https://www.bilibili.com/v/dance/otaku/#/") #对视频页面请求需要有Header
                c = url_otaku_dance.text
                s = re.sub('\n','', c)
                html_otaku_dance = etree.HTML(s)
                pattern_hot_tag = re.compile('<li title="(.*?)" class="tag-item">')
                hot_tag = html_otaku_dance.xpath('//*[@id="app"]/div[2]/div[2]/div[1]/div[2]/ul')[0].xpath('li')
                with open('hottag.txt', 'a+', encoding='utf8') as f:
                        f.write(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                        f.write('\n')
                        for tag in hot_tag:
                                tag_content = etree.tostring(tag).decode('utf8')
                                tag_name = pattern_hot_tag.findall(tag_content)
                                if len(tag_name) != 0:
                                        f.write(html.unescape(tag_name[0])) #专治中文显示为&#什么的
                                        f.write('\n')
                        f.write('----------------------------------------------')
                        f.write('\n')
                        f.write('----------------------------------------------')

        def get_up_info(self, mid):
                '''
                取得up主个人信息的函数
                '''
                up_url = "https://api.bilibili.com/x/space/acc/info?mid={}&jsonp=jsonp".format(mid)
                r = requests.get(url = up_url, headers = global_var.headers)
                up_info = json.loads(r.text)
                up_core_info = {}
                up_core_info["mid"]  = mid                     #数字
                up_core_info["up_name"] = up_info['data']['name'] #string
                up_core_info["sex"]  = up_info['data']['sex']  #string
                up_core_info["avatar"] = up_info['data']['face'] #string
                up_core_info["sign"]   = up_info['data']['sign'] #string
                return up_core_info


        def get_todo_list(self, aid):
                '''
                爬取一个video时，在网页里寻找其他备选目标插入TODO-LIST，相当于队列
                '''
                todo_in_v = []
                video_url = "https://www.bilibili.com/video/av{}".format(aid)
                response = requests.get(url=video_url, headers=global_var.headers)
                tree = etree.HTML(response.text)
                recommend = tree.xpath("//div[@class='card-box']")
                for r in recommend:
                        recommend_url = r.xpath("div[@class='info']/a")[0].attrib['href']
                        new_aid = int(re.findall('/video/av(\d*)/', recommend_url)[0])
                        todo_in_v.append(new_aid)
                return todo_in_v
        

        def get_danmaku_content(self, cid):
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
                        if counter < 250:  #只拿250条弹幕信息
                                c = elem.text
                                content += c
                                counter += 1
                        else: break
                return content


        def depth_craw(self, video_list):
                '''
                递归爬取，对一个av号的爬取会调用其他所有爬取信息的函数
                '''
                if len(video_list) == 0 : return  #递归出口
                if self.video_count % 50 == 0: time.sleep(0.5)
                depth_todo_list = [] #在爬取时新拿到的av号（每页基本上有20个推荐）
                for v in video_list:
                        video_url = "https://api.bilibili.com/x/web-interface/view?aid={}".format(v)
                        r = requests.get(url = video_url, headers = global_var.headers)
                        video_info = json.loads(r.text) #r.text是一个json样式的字符串，转换成字典
                        #if是handle特殊情况的，首先是稿件不存在错误，然后是分区不是宅舞错误
                        if video_info['message'] != "0" or video_info['data']['tname'] != "宅舞" : continue
                        else:  #以下信息，数字的都是纯数字
                                ###准备video表的信息###
                                video_core_info = {}
                                video_core_info["aid"] = v
                                video_core_info["cid"] = video_info['data']['cid']
                                video_core_info["mid"] = video_info['data']['owner']['mid']
                                video_core_info["video_name"] = video_info['data']['title']
                                video_core_info["up_name"]  = video_info['data']['owner']['name']
                                video_core_info["view"] = video_info['data']['stat']['view']
                                video_core_info["danmaku"] = video_info['data']['stat']['danmaku']
                                video_core_info["reply"]  = video_info['data']['stat']['reply']
                                video_core_info["favorite"] = video_info['data']['stat']['favorite']
                                video_core_info["coin"]    = video_info['data']['stat']['coin']
                                video_core_info["share"]   = video_info['data']['stat']['share']
                                video_core_info["like"] = video_info['data']['stat']['like']
                                video_core_info["history_rank"] = video_info['data']['stat']['his_rank']
                                video_core_info["pubtime"]      = video_info['data']['pubdate']
                                ###此处插入SQL-video###
                                self.mysql_manager.insert_video(video_core_info)
                                ###准备up表的信息###
                                up_core_info = self.get_up_info(video_info['data']['owner']['mid'])
                                ###此处插入SQL-up###
                                self.mysql_manager.insert_up(up_core_info)
                                ###准备danmaku表的信息###
                                '''
                                danmaku_content = self.get_danmaku_content(video_info['data']['cid'])
                                danmaku_core_info = {}
                                danmaku_core_info["aid"] = v
                                danmaku_core_info["cid"] = video_info['data']['cid']
                                danmaku_core_info["content"] = danmaku_content
                                danmaku_core_info["pubtime"] = video_info['data']['pubdate']
                                ###此处插入SQL-danmaku###
                                self.mysql_manager.insert_danmaku(danmaku_core_info)
                                '''
                                ###抓取相关推荐的aid### 
                                depth_todo_in_v = self.get_todo_list(v)
                                depth_todo_list += depth_todo_in_v   
                                ###数量自增###
                                self.video_count += 1
                                ###打印控制信息###
                                if self.video_count % 50 == 0: print("============{}is done============".format(self.video_count))
                               
                depth_todo_list_ = list(set(depth_todo_list)) #去除重复元素
                self.depth_craw(depth_todo_list_) #递归抓取
                return


        def get_max_page(self):
                '''
                当搜索“宅舞”时，会出现的最大页数
                '''
                search_otakudance_url = "https://search.bilibili.com/all?keyword=%E5%AE%85%E8%88%9E&from_source=banner_search&page=1"
                r = requests.get(url=search_otakudance_url, headers = global_var.headers)
                tree_ = etree.HTML(r.text.encode("utf8"))
                max_page_count = tree_.xpath("//li[@class='page-item last']/button")[0].text
                return int(max_page_count)


        def broad_and_depth_crawer(self):
                '''
                爬虫策略：在每轮首先广度搜索填充broad_todo列表，然后交给深度递归爬虫去爬，每轮重复，直到最大页数耗尽。
                '''
                max_page_count = self.get_max_page()
                for page in range(27,max_page_count):
                        broad_todo_list = []
                        search_otakudance_url = "https://search.bilibili.com/all?keyword=%E5%AE%85%E8%88%9E&from_source=banner_search&page={}".format(page)
                        r = requests.get(url=search_otakudance_url, headers = global_var.headers)
                        tree_ = etree.HTML(r.text.encode("utf8"))
                        search_result = tree_.xpath("//li[@class='video matrix']")
                        for video in search_result:
                                video_url = video.xpath('a')[0].attrib["href"]
                                aid       = int(re.findall('av(\d*)?', video_url)[0])
                                broad_todo_list.append(aid)
                        self.depth_craw(broad_todo_list)
                        print("================ PAGE {} DONE ==================".format(page))


        def dump_csv(self):
                self.mysql_manager.dump_csv()




        #已下两个函数用于给table表新增一列Pubtime，调用一次就够了:），是辅助函数
        def insert_col_time(self):
                self.mysql_manager.insert_video_time()
        def insert_time_content(self):
                rows = self.mysql_manager.get_time_content() #查询返回的是一个元组的列表
                for idx in range(len(rows)):
                        aid = rows[idx][0]
                        video_url = "https://api.bilibili.com/x/web-interface/view?aid={}".format(aid)
                        r = requests.get(url = video_url, headers = global_var.headers)
                        video_info = json.loads(r.text) #r.text是一个json样式的字符串，现在转换成字典可用             
                        if video_info['message'] != "0" : continue
                        else:
                            pubtime = video_info['data']['pubdate']
                            self.mysql_manager.insert_time_content(aid, pubtime)
                            print(idx)
                        
               
                
            









if __name__ == "__main__":
    penta = OtakuDanceSpider()
    #penta.broad_and_depth_crawer()
    penta.dump_csv()
  
    


   