# -*- coding: utf-8 -*- 
# @Time : 2024/10/24 下午2:55
# @Author : zhaomeng
# @File : task_status.py
# @desc: 定时巡检所有的开启了监控的主机节点，运行任务检查，任务完成，更新数据库>检查任务状态后执行发送邮件通知
import time

import django
import os
import traceback
import sys
from datetime import datetime
import multiprocessing
sys.path.extend(['/mnt/data/pythongit/CrawlSpace版本迭代/CrawlSpace'])
os.environ['DJANGO_SETTINGS_MODULE'] = 'CrawlSpace.settings'
django.setup()
from spider.models import Client
from spider.models import TaskStatusList
from spider.views import task_status
import logging


def task_status_info():
    """
    使用这个20241028
    :return:
    """
    start = time.time()
    result = Client().get_enable_client()
    if result:
        print(result)
        for client_id in result:
            logging.warning(client_id)
            result = TaskStatusList().get_task_info(client=client_id)
            print(result)
            if result:
                spider_tasks = []
                for inf in result:
                    print(inf)
                    item = {
                        "client_id": inf[0],
                        "project": inf[-1],
                        "jobid": inf[1]
                    }
                    logging.warning(item)
                    status = task_status(client_id=item.get("client_id"), project=item.get("project"),
                                         jobid=item.get("jobid"))
                    print(status)
                    task = TaskStatusList.objects.filter(jobid=item.get("jobid")).values('end_time', "status").first()
                    print(task.get("end_time"))
                    try:
                        if status == "finished" and not task.get("end_time"):
                            # 任务完成及没有添加完成任务的时间就修改status为finished并更新最后的完成时间
                            try:
                                # 状态设置完成并写入列表
                                TaskStatusList.objects.filter(jobid=item.get("jobid")).update(
                                    end_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'), status="已完成")
                                spider_tasks.append(item)
                            except Exception as e:
                                # print(e)
                                logger.error(str(e))
                        elif task.get("status"):
                            # 如果状态已经是完成的则加入列表
                            spider_tasks.append(item)
                    except AttributeError:
                        """删除的时候，任务在加载，会存在获取到的数据已经被删除的情况"""
                        pass
                    finally:
                        print(spider_tasks)

    end = time.time()
    print(f"本地巡检花费时间：{end - start}")


def task_info(client_id):
    result = TaskStatusList().get_task_info(client=client_id)
    if result:
        spider_tasks = []
        for inf in result:
            item = {
                "client_id": inf[0],
                "project": inf[-1],
                "jobid": inf[1]
            }
            logging.warning(item)
            status = task_status(client_id=item.get("client_id"), project=item.get("project"),
                                 jobid=item.get("jobid"))
            task = TaskStatusList.objects.filter(jobid=item.get("jobid")).values('end_time', "status").first()
            try:
                if status == "finished" and not task.get("end_time"):
                    TaskStatusList.objects.filter(jobid=item.get("jobid")).update(
                        end_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'), status="已完成")
                    spider_tasks.append(item)
                elif task.get("status"):
                    spider_tasks.append(item)
            except AttributeError:
                pass
            finally:
                print(spider_tasks)


def task_status_info_v():
    """
    多进程处理20241028测试是与单进程没啥区别
    :return:
    """
    start = time.time()
    result = Client().get_enable_client()
    if result:
        print(result)
        with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
            pool.map(task_info, result)
    end = time.time()
    print(f"本地巡检花费时间：{end - start}")


# 调用函数
# task_status_info_v()

task_status_info()
