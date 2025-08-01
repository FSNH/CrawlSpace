# 建立 python3.7 环境
FROM python:3.7
# 镜像作者
MAINTAINER zhaomeng
# 设置 python 环境变量
ENV PYTHONUNBUFFERED 1
# 设置pip源为国内源
COPY pip.conf /root/.pip/pip.conf
# 在容器内创建CrawlSpace文件夹
RUN mkdir /CrawlSpace
# 设置容器内工作目录
WORKDIR /CrawlSpace
# 将当前目录文件加入到容器工作目录中（. 表示当前宿主机目录）
ADD . /CrawlSpace
EXPOSE 8000
# pip安装依赖
RUN pip install -r requirements.txt
# 挂在配置文件的路径及项目路径，需要run的时候挂载到宿主机
VOLUME ["/CrawlSpace/spider/configs", "/CrawlSpace/spider/project"]
# gunicron
# 赋予操作权限
RUN chmod +x /CrawlSpace/crawlspacex.sh
CMD /bin/bash /CrawlSpace/crawlspacex.sh start