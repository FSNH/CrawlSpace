# -*- coding: utf-8 -*- 
# @Time : 2023/8/11 下午5:07
# @Author : zhaomeng
# @File : urls.py.py
# @desc:
from django.urls import path, re_path
from . import views

app_name = "monitor"
urlpatterns = [
    path("index.html", views.index, name="index"),  # 邮箱配置页面
    path("configs/", views.emailinfo, name='configs'),  # 配置信息
]
