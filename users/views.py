
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse

from users.form import LoginForm


# Create your views here.

def login_view(request):
    # 判断是否是POST请求
    form_obj = LoginForm()
    if request.method == 'POST':
        form_obj = LoginForm(request.POST)
        if form_obj.is_valid():
            name = form_obj.cleaned_data.get("username")
            password = form_obj.cleaned_data.get("pwd")
            # authenticate会把POST里面的用户名和密码与auth_user表里面用户和密码对比
            # 如果比对成功会返回用户名，如果对比失败会返回None
            user = authenticate(username=name, password=password)
            # 判断user是否为True
            if user:
                # user如果为True，则使用login把user储存在session里面
                login(request, user)
                # 转到spider.html(首页)
                return redirect(reverse("spider:nodeindex"))
            else:
                return HttpResponse('用户或密码填写错误')
    else:
        return render(request, 'users/login.html', {"form_obj": form_obj})


def logout_view(request):
    logout(request)
    # 重定向反向解析到登录页
    return redirect(reverse("users:login"))
