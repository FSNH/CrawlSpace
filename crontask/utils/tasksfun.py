""""
执行定时任务的运行逻辑函数
"""
import json
import logging

from spider.models import Client, TaskStatusList
from spider.utils.scrapydconf import get_scrapyd
from spider.utils.getjson import get_code

logger_crontask = logging.getLogger('crontask_log')


def excute_task(args, **kwargs):
    """
    执行规则爬虫的的定时任务
    :param args: 函数的参数
    :return:
    """
    print(kwargs)
    client_id = kwargs.get('client_id')
    data = get_code(kwargs.get("name"))  # 获取json文件
    print(data)

    if data.get("status") == 200:
        client = Client.objects.get(id=client_id)
        scrapyd = get_scrapyd(client)
        data = data.get('code')
        data = data.replace("true", "True").replace('false', 'False').strip()  # json数据的bool值替换
        data = eval(data)
        jobid = scrapyd.schedule(project="quote", spider=data.get("spider"),
                                 **{"data": json.dumps(data)})
        # print(jobid)
        TaskStatusList.objects.create(project='quote', spidername=data.get("spider"),
                                      rulefile=data.get("name"), status="",
                                      jobid=jobid, client=client)
        logger_crontask.info(f"{TaskStatusList}:规则爬虫项目运行成功!")
        pass


def excute_spider(args, **kwargs):
    """
    执行scrapy爬虫的定时任务
    :param args:
    :return:
    """
    # print(kwargs)
    client_id = kwargs.get('client_id')
    project = kwargs.get('project')
    spidername = kwargs.get('name')
    client = Client.objects.get(id=client_id)
    scrapyd = get_scrapyd(client)
    jobid = scrapyd.schedule(project=project, spider=spidername)
    # print(jobid)
    TaskStatusList.objects.create(project=project, spidername=spidername,
                                  rulefile="", status="",
                                  jobid=jobid, client=client)
    logger_crontask.info(f"{TaskStatusList}:SCRAPY项目运行成功!")
    pass

