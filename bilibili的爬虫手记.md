对视频页面的直接请求需要登录，否则403。


统计各种数据的文件路径：https://api.bilibili.com/x/web-interface/archive/stat?aid=3470509
浏览器可以直接打开，这是个json文件，可以直接打开，只要构造合适的HEADER：

Accept: */*
Accept-Encoding: gzip, deflate, br
Accept-Language: zh-CN,zh;q=0.9
Connection: keep-alive
Host: api.bilibili.com
Origin: https://www.bilibili.com
Referer: https://www.bilibili.com/video/av3470509
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36




视频所有基本信息（包含上面的）：https://api.bilibili.com/x/web-interface/view?aid={3470509}
判断宅舞区？ data{tname:"宅舞"

弹幕加载：
首先从所有信息里面提取cid（chat id）   data{cid:}
https://api.bilibili.com/x/v1/dm/list.so?oid={5512781}  这里的oid == cid
是xml文件，正则提取信息存入

视频的各种标签https://api.bilibili.com/x/tag/archive/tags?callback=jqueryCallback_bili_08256477461606648&aid=3470509&jsonp=jsonp&_=1549374630511
这个好像直接访问是403
获取视频标签的方法：在网页里提取正则？
//*[@id="v_tag"]这个是标签区块div的XPATH，每个标签都是li,li里面是<a>tag</a>
//*[@id="v_tag"]/ul/li[1]/a
评论和标签一样都不在/x/web-interface/路径下所以不能直接爬取，只能模拟登录之后下载网页看


相关链接：https://api.bilibili.com/x/web-interface/archive/related?aid={3470509}&jsonp=jsonp
