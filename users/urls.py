from django.urls import path, re_path
from . import views

app_name = 'users'
urlpatterns = [
    path('', views.login_view),  # 首页登录
    re_path(r'^login/$', views.login_view, name='login'),  # 登录
    re_path(r'^logout/$', views.logout_view, name='logout'),  # 退出
]
