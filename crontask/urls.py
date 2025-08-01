from django.urls import path, re_path
from . import views

app_name = "cron"
urlpatterns = [
    path("create/", views.cron_task, name="create"),  # 创建定时任务
    path("del/", views.deltask, name="deltask"),  # 删除定时任务
    path("list.html", views.index, name="cronindex"),  # 查看定时任务
    path("info/", views.taskinfo, name="taskinfo"),  # 任务运行信息
    path(r"info/<str:rulename>", views.croninfo, name="configuation"),  # 任务配置信息
    path(r"pause/<str:rulename>", views.cancel_cron, name="cancel"),  # 暂停任务
    path(r"resume/<str:rulename>", views.restart_cron, name="restart"),  # 重启任务
    path(r"jobinfo/<str:rulename>", views.jobinfo, name="jobinfo"),  # 任务信息
    path('re_sche/<str:rulename>/',views.re_sche,name="scheduler")  # 重启服务后重新调度任务
]
