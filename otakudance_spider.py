import requests
import re
from lxml import etree
import time
import html
def get_hot_tag():
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
                    
    

if __name__ == "__main__":
    get_hot_tag()