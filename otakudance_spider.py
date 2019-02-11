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


        def get_video_info(self, video_list):
            '''
            递归爬取，对一个av号的爬取会调用其他所有爬取信息的函数
            '''
            if len(video_list) == 0 or self.video_count > global_var.max_video_count: return  #递归出口
            if self.video_count % 100 == 0: time.sleep(global_var.crawer_sleep_time) #每隔一段时间休息一次
            todo_list = [] #在爬取时新拿到的av号（每页基本上有20个推荐）
            for v in video_list:
                video_url = "https://api.bilibili.com/x/web-interface/view?aid={}".format(v)
                r = requests.get(url = video_url, headers = global_var.headers)
                video_info = json.loads(r.text) #r.text是一个json样式的字符串，现在转换成字典可用
                if video_info['data']['tname'] != "宅舞": continue
                else:  #以下信息，数字的都是纯数字，不是数字字符串型
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
                    #此处插入SQL
                    self.mysql_manager.insert_video(video_core_info)
                    up_core_info = self.get_up_info(video_info['data']['owner']['mid'])
                    #此处插入SQL
                    self.mysql_manager.insert_up(up_core_info)
                    todo_in_v = self.get_todo_list(v)
                    todo_list += todo_in_v
                    if self.video_count % 10 == 0: print("============{}/{} is done============".format(self.video_count, global_var.max_video_count))
                    self.video_count += 1
            todo_list_ = list(set(todo_list)) #去除重复元素
            self.get_video_info(todo_list_) #递归抓取
            return

        def dump_csv(self):
                self.mysql_manager.dump_csv()
                    

               
                
            









if __name__ == "__main__":
    penta = OtakuDanceSpider()
    v = [1759101]
    #penta.get_video_info(v)
    penta.dump_csv()
    


   