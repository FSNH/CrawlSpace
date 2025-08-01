# CrawlSpace
CrawlSpace爬虫管理系统(博客介绍)
http://zhaomeng.net.cn/articles/s45.html
## 本地调试运行

```
# 创建虚拟环境
conda create-n crawlsapce python=3.7
conda activate crawlspace  # 进入环境
pip install -r requirements.txt  # 安装依赖库
python manage.py runserver 0.0.0.0:8000

```
浏览器输入：127.0.0.1:8000/accounts/或者127.0.0.1:8000

初始账号：admin01 密码：admin01
## CrawlSpace爬虫部署框架介绍

CrawlSpace全新的爬虫部署框架，为了适应工作的爬虫部署的使用，需要自己开发一个在线编写爬虫及部署爬虫的框架，框架采用的是Django2.2+bootstap依赖scrapyd开发的全新通用爬虫在线编辑部署及scrapy项目的部署框架。项目实现的五大块的功能及许多在维护爬虫的过程中用的许多实用的操作功能。

首页通用爬虫的模块编写采集全站的数据：

![image](http://zhaomeng.net/media/images/2022/10/16/image-20221016172703-1.png)
爬虫项目的运行列表
![image](http://zhaomeng.net/media/images/2022/10/22/1987692026.jpg)
日志结果查看
![image](http://zhaomeng.net/media/images/2022/10/16/udfxhn.png)
定时任务列表
<img width="1553" height="199" alt="定时任务列表" src="https://github.com/user-attachments/assets/852e4008-866b-4ee7-b930-44ab7456e820" />
任务配置查看
![image](http://zhaomeng.net/media/images/2022/10/16/image-20221016174825-5.png)
主机信息列表
![image](http://zhaomeng.net/media/images/2022/10/16/image-20221016175127-6.png)
主机创建
<img width="1164" height="542" alt="主机创建" src="https://github.com/user-attachments/assets/77468b32-7937-44c7-b91b-d62c61dc65a3" />
项目打包及部署
<img width="1578" height="627" alt="打包部署" src="https://github.com/user-attachments/assets/1a0c3300-104e-4d26-96cd-5c84d0de911f" />
项目调度
![image](http://zhaomeng.net/media/images/2022/10/16/image-20221016180138-1.png)
定时任务设置
![image](http://zhaomeng.net/media/images/2022/10/16/image-20221016180306-2.png)
scrapy项目在线编辑
![image](http://zhaomeng.net/media/images/2022/10/16/image-20221016180529-3.png)
节点可视化监控，支持在线检测主机状态并提示功能
![image](http://zhaomeng.net/media/images/2024/06/06/1717667624827.jpg)
邮箱通知功能
<img width="1522" height="710" alt="邮箱通知" src="https://github.com/user-attachments/assets/2e67ae9b-3cea-45f4-b522-5ed5ca1652dd" />
项目仓库地址
<img width="1146" height="528" alt="项目仓库" src="https://github.com/user-attachments/assets/c98bfda0-1954-44fb-9368-9d78eed4655d" />
通用爬虫月度数据源可视化统计（自定义数据）
![image](http://zhaomeng.net/media/images/2024/06/06/1717667809510.png)

以上就是crawlspace的功能，相比其他的部署，这个部署框架更加的便于维护爬虫项目，操作更加灵活方便，交互更加便捷舒适，功能更加完善，信息的显示更加清晰，同时支持手机端在线操作！
![扫码_搜索联合传播样式-白色版](https://github.com/user-attachments/assets/3d824ba7-89b3-407b-ae74-a3822f670b85)

## Docker项目部署

```
项目根目录下创建镜像crawlspace：
docker build -t crawlspace .
创建容器：
mkdir -p /crawlspace/spider/configs
mkdir -p /crawlspace/spider/project
docker run -d -p 8000:8000 --name crawlspace --restart=always -v /crawlspace/spider/configs:/CrawlSpace/spider/configs -v /crawlspace/spider/project:/CrawlSpace/spider/project crawlspace:latest

```


## 本地运行
```
./crawlspacex.sh start
```
## 本地停止
```
./crawlspacex.sh stop
```
