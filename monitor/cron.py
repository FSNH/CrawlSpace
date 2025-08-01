# -*- coding: utf-8 -*- 
# @Time : 2023/8/11 下午3:23
# @Author : zhaomeng
# @File : cron.py
# @desc: 检查任务完成后，发送邮件通知(邮件通知只在当日)
import django
import os
import traceback
import sys

sys.path.extend(['/mnt/data/pythongit/CrawlSpace版本迭代/CrawlSpace'])
os.environ['DJANGO_SETTINGS_MODULE'] = 'CrawlSpace.settings'
django.setup()
from django.conf import settings
from spider.models import TaskStatusList
from monitor.models import Notification, EmailInfo
# Create your views here.
from django.core.mail import send_mail
import datetime
from django.utils import timezone

now_time = timezone.now()


# 邮件配置
def async_monitor_spider_status():
    subject = ""
    recipient_list = ""
    from_email = ""
    content = ""
    interval_send_email = ""
    host = ""  # 服务器域名
    emailinfos = EmailInfo.objects.all()
    print(emailinfos)
    for emailinfo in emailinfos:
        # settings邮件配置
        settings.EMAIL_ENABLED = emailinfo.email_enable
        settings.EMAIL_HOST_PASSWORD = emailinfo.email_host_pwd
        settings.EMAIL_PORT = emailinfo.email_port
        settings.EMAIL_HOST_USER = emailinfo.email_host
        settings.EMAIL_HOST_PASSWORD = emailinfo.email_host_pwd
        settings.EMAIL_USE_TLS = emailinfo.tls
        settings.DEFAULT_FROM_EMAIL = emailinfo.default_from_email

        # 邮箱内容配置
        subject = emailinfo.subject
        recipient_list = emailinfo.recipient_list.split(",")
        from_email = emailinfo.from_email
        content = emailinfo.html_message
        interval_send_email = {emailinfo.unit: int(emailinfo.interval_send_email)}
        print(interval_send_email)
        host = emailinfo.host

    print('爬虫监控运行中。。。。。。')
    try:
        if settings.EMAIL_ENABLED:
            tasklist = TaskStatusList.objects.filter(notifications_enable=1)  # 查询所有启用邮件通知的任务
            print(tasklist)
            if tasklist:
                for kk in tasklist:
                    if kk.end_time and kk.status == "已完成":
                        notification_url = f"{host}/spider/notification/{kk.jobid}/2/"
                        message = content.format(kk.client.name, kk.project, kk.spidername, kk.rulefile,
                                                 kk.jobid, kk.status,
                                                 kk.start_time, kk.end_time, notification_url)
                        obj = Notification.objects.filter(jobid=kk.jobid).order_by('-create_time')
                        if not obj:
                            # 不存在该记录
                            try:
                                Notification.objects.create(client=kk.client.name,
                                                            project=kk.project,
                                                            spidername=kk.spidername,
                                                            rulefile=kk.rulefile,
                                                            jobid=kk.jobid,
                                                            status=kk.status,
                                                            start_time=kk.start_time,
                                                            end_time=kk.end_time
                                                            )
                                send_mail(subject=subject, message="", from_email=from_email,
                                          recipient_list=recipient_list,
                                          html_message=message)
                            except Exception as e:
                                print(traceback.print_exc())
                                Notification.objects.filter(jobid=kk.jobid, ).update(email_status="失败",
                                                                                     msg=str(e))
                            else:
                                Notification.objects.filter(jobid=kk.jobid, ).update(email_status="成功", msg=message)
                                print("邮件发送成功")
                        else:
                            # 存在该记录，判断当前时间-通知表的创
                            # 建时间（最后一次)>=3小时
                            create_at = obj[0].create_time  # 通知表创建时间
                            time_difference = now_time - create_at
                            delta = ''
                            if interval_send_email.get("hour", ""):
                                delta = datetime.timedelta(hours=interval_send_email.get("hour"))
                            elif interval_send_email.get("minutes", ""):
                                delta = datetime.timedelta(minutes=interval_send_email.get("minutes"))
                            elif interval_send_email.get("days", ""):
                                delta = datetime.timedelta(days=interval_send_email.get("days"))
                            print(delta,time_difference)
                            if time_difference >= delta:  # 差值大于3小时的，发送邮件通知处
                                try:
                                    Notification.objects.create(client=kk.client.name,
                                                                project=kk.project,
                                                                spidername=kk.spidername,
                                                                rulefile=kk.rulefile,
                                                                jobid=kk.jobid,
                                                                status=kk.status,
                                                                start_time=kk.start_time,
                                                                end_time=kk.end_time
                                                                )

                                    send_mail(subject=subject, message="", from_email=from_email,
                                              recipient_list=recipient_list,
                                              html_message=message)
                                except Exception as e:
                                    print(traceback.print_exc())
                                    Notification.objects.filter(jobid=kk.jobid, ).update(email_status="失败",
                                                                                         msg=str(e))
                                else:
                                    Notification.objects.filter(jobid=kk.jobid, ).update(email_status="成功", msg=message)
                                    print("邮件发送成功")
                            else:
                                # 爬虫通知还没有到设置的时间间隔
                                pass
                    else:
                        print("爬虫运行正常！")
            else:
                pass
        else:
            print("爬虫邮件通知没有开启！")
    except Exception as e:
        print(traceback.print_exc())


async_monitor_spider_status()