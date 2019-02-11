对视频页面的直接请求需要登录，否则403。除非拿Headers


#统计各种数据的文件路径：https://api.bilibili.com/x/web-interface/archive/stat?aid=3470509
视频所有基本信息及相似推荐的信息（包含上面的）：https://api.bilibili.com/x/web-interface/view?aid=3470509
通过一个这个进行宽度+深度爬取，效率高。
判断宅舞区？ data{tname:"宅舞"
浏览器可以直接打开，这是个json文件，可以直接打开，只要构造合适的headers：

headers = {
    'accept': "*/*",
    'accept-encoding': "gzip, deflate, br",
    'accept-language': "zh-CN,zh;q=0.9",
    'cookie': "fts=1540638084; sid=92vilnfj; im_notify_type_24004198=0; stardustvideo=1; CURRENT_FNVAL=16; buvid3=A7C42C7F-478E-4442-BA3B-D8369FCFEA4A85380infoc; finger=54bdb683; rpdid=iwpiqsoqqmdospqkmxliw; UM_distinctid=1689cfd3e859c-03c64df1f82fa7-10346654-13c680-1689cfd3e86ad; dssid=921k2ef72d9610ceb; dsess=BAh7CkkiD3Nlc3Npb25faWQGOgZFVEkiFTJlZjcyZDk2MTBjZWJjZjMGOwBG%0ASSIJY3NyZgY7AEZJIiU5NDdkYzkwNjQyZTczZGNjZDhjYzgxNzNkODQ3NWQ5%0AZAY7AEZJIg10cmFja2luZwY7AEZ7B0kiFEhUVFBfVVNFUl9BR0VOVAY7AFRJ%0AIi05MGEyOTUwODRjMjMyZDBjZjAwMjNlNWUyZDRiZDkzOWYxYjY0YWQ2BjsA%0ARkkiGUhUVFBfQUNDRVBUX0xBTkdVQUdFBjsAVEkiLWJiMGUwM2Q3ZWEyZDk4%0AYTc1ODA4YmNkYmIxNzgxYWExYmI4NjA0ZTQGOwBGSSIKY3RpbWUGOwBGbCsH%0A%2FUBUXEkiCGNpcAY7AEYiEjYwLjE5LjIwOC4xNzM%3D%0A--b16e19ade3ae0f642b6bf28c27d4b4add7a7092c; CURRENT_QUALITY=80; LIVE_BUVID=10baf6782c9b0d5da280886005e1e5c9; LIVE_BUVID__ckMd5=309ada07cb7818d5; bp_t_offset_24004198=218818464789952412; _dfcaptcha=66a9015c01a215cef26c43eae9d86aa7; DedeUserID=24004198; DedeUserID__ckMd5=105a13f636e3cdad; SESSDATA=215ee48a%2C1552406888%2Cf8a14d21; bili_jct=3b586533c7bbb94f7d6e3d1cef42e04b",
    'origin': "https://www.bilibili.com",
    'referer': "https://www.bilibili.com/",
    'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
    'cache-control': "no-cache"
    }

不知道这个cookie过期是啥时候




#弹幕加载：
首先从所有信息里面提取cid（chat id）   data{cid:}
https://api.bilibili.com/x/v1/dm/list.so?oid=5512781  这里的oid == cid
是xml文件，正则提取信息存入

视频的各种标签https://api.bilibili.com/x/tag/archive/tags?callback=jqueryCallback_bili_08256477461606648&aid=3470509&jsonp=jsonp&_=1549374630511
这个好像直接访问是403
获取视频标签的方法：在网页里提取正则？
//*[@id="v_tag"]这个是标签区块div的XPATH，每个标签都是li,li里面是<a>tag</a>
//*[@id="v_tag"]/ul/li[1]/a
相关链接：https://api.bilibili.com/x/web-interface/archive/related?aid=3470509&jsonp=jsonp

#评论
不在/x/web-interface/路径下所以不能直接爬取，登录之后拿到headers就能为所欲为了。headers在登录之后第一个返回的web?文件里面有（很多都有）
https://api.bilibili.com/x/v2/reply?callback=jQuery17209138192109065575_1549815219104&jsonp=jsonp&pn=1&type=1&oid={43052280}&sort=0&_=1549815340648
oid换成对应的av号就能拿到一个很奇怪的文件，只有一点点评论，怎么把数量提高？ 提取评论的正则： "message":"(.*?)"
我知道怎么提高了！妈的由于数量过于庞大没有加载完全！加载全了就出来了。但数量也不多，推测可能与时间有关？

或者拿着刚才的headers直接请求视频页面，可以拿到评论总数和几个热门评论。这个页面的评论被抹去了，可见评论一定是异步加载。
但是它放在哪儿了呢。。。

#up个人信息：
https://api.bilibili.com/x/space/acc/info?mid=3974880&jsonp=jsonp  注意用的是mid

