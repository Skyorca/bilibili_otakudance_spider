Hello，我（女性的“她”）是一只bilibili的小爬虫，专门爬取舞蹈区->宅舞区的数据并进行可视化分析~
该项目纯粹是为了自己的兴趣，因为本人也是宅舞区的up主，一名小舞见。第一次写爬虫并做数据统计，算是刚上路的萌新；寒假恰好学习了小象学院的爬虫课程，所以这也是自己给自己布置的大作业。说起来，对宅舞区分析的想法半年前的暑假就有了，只不过寒假才得以实现。
这个文章可以当做学校实验课的实验报告来阅读。该项目会不断进化，完善代码，增强爬虫能力，并做更多的统计分析。

一 分析bilibili网站结构
首先“君子协议” robots.txt是禁止所有爬虫爬取服务器的任何目录的。但是...是吧！
sitemap.xml可以明确看出网站层次架构。不过对我这种专门分析一个视频区的来说不重要。
接下来的东西很重要：

1. 统计各种数据的文件路径：https://api.bilibili.com/x/web-interface/view?aid={视频av号}

视频所有基本信息以json的形式展示出来，主要包括视频的各种统计信息（代码里面video字典的键都在这里，比如分区信息tname，播放量view，回复数reply，等等）。从代码可以看到我提取了14项基本数据作为一个视频的特征。
注意：一般message都是等于“0”（字符0）的，否则表示视频不存在，需要过滤掉。
我判断它是否属于宅舞区的标志是tname="宅舞"。
它不需要特殊的Headers即可访问。

2. 弹幕内容 https://api.bilibili.com/x/v1/dm/list.so?oid={视频的cid}

首先要知道一个视频有三个数字串来定位：aid(也就是av号)，mid(up主的标号，对up唯一)，cid（该视频对应的弹幕文件的标号，对每个视频唯一）。mid和cid都能从第一条里面的json提取到。拿到cid填进去这个url就能拿到弹幕文件，是xml格式。我通过etree的方式提取所有弹幕正文，并习惯于把它们拼接为一个大字符串，作为分析函数的输入。
它不需要特殊的Headers即可访问。

3. 对视频页面直接访问以及爬取评论的说明

要知道的是，通过爬虫直接访问某个视频页面是403的，所以要带上headers。在浏览器先登录一下，之后从Inspect--Network找到get到的许多网页，它们都有headers这块，拿过来就好了。最重要的是里面的cookies，它的有效期好像很长，所以基本上拿一次headers就够了。
这样爬下的页面也是不完整的：能得到页面右侧的“推荐列表”但拿不到评论。只能在页面的一开始拿到几条热门评论。找来找去也不知道评论是怎样异步加载的。但是偶然发现了一个json文件：
https://api.bilibili.com/x/v2/reply?callback=jQuery17209138192109065575_1549815219104&jsonp=jsonp&pn=1&type=1&oid={43052280}&sort=0&_=1549815340648
注意oid={}填上正确的cid号。这个json文件能拿到40+条评论，显然是不全的。那怎么拿全部的？怀疑与时间有关，也就是上述的url带有时间参数，可能是“返回在时间t1到时间t2之间的评论”。那么只要不断更新t1 t2就能拿到全部评论了。熟悉unix时间戳的童鞋应该一眼就看出来上面的url里有两个类似时间戳的东西：
1549815219(104)---->2019-02-11 00:13:39
1549815340(648)---->2019-02-11 00:15:40
后三位是多出来的digits。但是具体还不知道设置规则，也没有去做实验。可以作为后续工作。

4. up个人信息：
https://api.bilibili.com/x/space/acc/info?mid={up的mid}&jsonp=jsonp  注意用的是mid
不需要headers，进去可以拿到静态基本信息，比如名字，性别，头像，生日，是不是会员等等。但是关注数，粉丝数是拿不到的，奇怪的是可以拿到对方的硬币数...
需要说明的是爬虫访问up个人空间主页是基本拿不到东西的。也就是说现在还不能做到“以某个up为中心，集中爬取它的所有视频”。

网站内容暂时探讨到这里，接下来谈谈我的实现方法。


二 具体实现

一开始我在本地写代码，是单线程爬虫，并把下载结果存储在MySQL里面。环境：MacBookPro(好多年前的)配置anaconda，并专门有一个虚拟环境，在anaconda自带的vscode里写代码。目前我开了多线程爬虫（随便设了一个20），并放在云服务器上跑，结果也放在云服务器上的MySQL里，7*24小时无压力。准备最后把dump结果拷回本地。

第一步：爬虫策略
当自己真正爬数据时才体会到老师说的深度与广度两种策略选择的重要性。一开始我的思路是手工选择一个包含一些宅舞视频av号的列表，然后以它们为基础实现广度爬取：
依次处理初始列表中的视频，每次处理完访问它的视频页面拿到相应的推荐列表（大概五个左右）塞到to_do列表里。依据是宅舞视频的推荐列表基本都是宅舞。那么当初始列表都处理完毕后，就得到了一个to_do列表，把它作为新的初始列表递归爬取。就像一个队列一样。我才意识到我只不过用了递归函数而已，并不是真正意义上的“递归爬取”。因为递归爬取应该是“处理完一个链接后马上处理它指向url的下一个链接”，而我是用队列管理的，所以应该是广度优先，只不过使用了递归函数。
但是这里的递归函数有个缺陷：我设置的出口是to_do list为空，而这种情况是几乎不会出现的，也就是递归基本不会停止，但一开始时发现确实爬了一些就退出，不知道为啥。
而且当我试图用内部成员video_count限制每次运行爬取数量时（要限制是因为一开始还在摸索阶段）也并不奏效。不过这个递归函数不会爆栈，只会一直运行下去，所以暂时勉强能接受这个缺点。
手工设计初始列表多麻烦，后面我找到了一种简便的方法：搜索关键词“宅舞”能返回一个最大页数=50（目前是这样）的页面，而且页数是作为参数放在url里的，那么我就可以先拿到最大页数，然后以页数做循环，每次循环填充一个to_do_list，也就是该页面能拿到的所有视频；然后把它作为初始列表传给上一个“伪”递归函数去做爬取。当然这样一来每个页面的停留时间可能很长很长甚至无限（关键在于那个“伪”递归函数没有准确的出口）。不过也不影响，毕竟我们只是要求一定数量的样本而不是全部的。我们可以假定当page x已经爬取了10w个链接时就认定该页已经爬完，exit。
以上构成了两个核心函数： broad_and_depth_crawer()调用depth_crawer(),注意这个depth并不是真的深度优先策略。
后来学了多线程，发现这东西使速度起飞必须要引进啊。那我就对每页单开一个线程跑，也就是我一次开20线程的话就一次并行爬20页的东西。注意别忘了把mysql的连接池大小也设置成20。然后对以上两个核心函数进行多线程改造，形成了multithread_broad_and_depth_crawer()调用multithread_depth_crawer()两个函数。多线程思路来自小象学院的课程代码，非常有效，起飞了十倍不止。

第二步：数据存储
延续了小象学院课程的思路，使用MySQL存储数据。otakudance_spider.py调用mysql_manager.py实现与MySQL的交互，包括：从零开始创建数据库，创建数据表，插入数据，导出数据。我没用pymysql这个库，用的是mysql-connector。我觉得它支持多线程的策略很好：它会创建一个连接池，比如size=20的连接池，这样我去跑20线程就恰好一个线程用一个端口，不多不少刚刚好。其实上课时还没意识到连接池多有用，自己跑时才意识到，并且一开始出现了 线程数>连接池size 的情况，是因为连接池忘了开大点。
实例化OtakuDanceSpider类时，init方法实例化MySQLManager类，而它的init方法会做从零开始创建数据库和创建数据表的操作。第二次实例化OtakudanceSpider时，即往后运行otakudance_spider.py时，会提示video表已经存在，不过没有什么影响。
很多注意事项我都在mysql_manager.py里进行了标注，以“###1”等的形式。这里我说一下踩过的坑吧。
1）一开始忘了加入“pubtime”也就是每个视频的发布时间。后来写了好几个辅助函数把它给填上（好在发现那会儿数据量不大）。包括danmaku表也是后来用辅助函数加上去的。
所以一开始设计数据表的结构很重要，之后弥补很麻烦！而数据表与需求相关，所以一开始要把想解决的问题基本上想全了。
2）我一开始不熟悉mysql语法所以是乱打乱撞一点点学会的。建议熟悉mysql基本操作再来写代码。比如update是更新（也就是修改已有的或向已有的空白块里填）某一’块‘或某几’块‘，我新建时间列后对每个视频填入时间就是update。而insert是插入一行新的数据。一开始总搞混它们。
3）Mac的Mysql配置
 /usr/local/var/mysql 是mysql存放数据的路径
 /usr/local/Cellar/mysql/8.0.12/.bottle/etc/my.cnf 配置文件路径 这个
4）mysql导出数据（dump）操作涉及一个路径问题，在mysql里执行 show variables like '%secure%'; 查看secure-file-priv是不是为NULL。如果不是NULL就把输出路径指定为这个就行了。如果是NULL要修改一下。把上面那个my.cnf修改后放到/private/etc下面,再重启mysql服务器才生效（restart mysql.server）。不同系统my.cnf路径不同，大家自己摸索吧。win下还是my.ini。另外注意my.cnf的格式，否则报错。

第三步：放到云端
总不能电脑一直开机，而且数据量也要上去，所以萌生了搬到云上的念头。我买的是腾讯云一个月10块钱最便宜的那种，ubuntu16.04。基本上够用了。
首先要配置服务器环境。主要是安装各种需要的python3包和mysql服务。mysql服务怎么安装搜一下就有了，下载三个东西就行。可能你要先升级一下pip3，但是我升级后遇到了一个pip3版本的问题，这个出错后搜一下就有解决方案，也可以用python3 -m pip来替代pip3指令。可以在本地用pip3 freeze > requirements.txt导出需要的包然后传到云端，在云端用pip3 -r requirements.txt自动地一行行安装包。
还有一个很辣鸡的mysql dump问题。它写好了secure-file-priv为/var/lib/mysql-files/，但是我一开始没有权限访问它，就傻了，su显示授权失败。后来发现了要先sudo -i切换到root就能访问了。然后以root身份在mysql-files下执行拷贝命令cp video.csv ~/bilibili_dump/就能把root的文件拿到普通用户区，然后就能ssh拷贝到本地了。
最后一个就是：如何在我关闭terminal后爬虫继续运行？不然关闭terminal发送的挂起信号会中断目前的进程。经过尝试发现screen大法好：
执行 screen 切换到screen进程界面
正常python3运行爬虫，看到已经运行了，先组合键contral+a进入命令模式，然后键入d，挂起这个screen进程，在后台跑去。
在正常的用户界面执行 screen -ls查看你的screen 的pid
之后关闭终端就没问题了。
下次回来时， screen -r pid就可以看到正在后台跑的数据了。反正Mysql服务器也不关，一直写去吧。虽然这个最简单的服务器性能比我的MAC还差，不过它可以7*24啊，一天8w不是问题。 




