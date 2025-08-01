from django.urls import path, re_path
from . import views

app_name = "analysis"
urlpatterns = [
    path("index.html", views.index, name="index"),  # 分析首页
    path("sum_increase_update/", views.get_data, name="get_data"),  # 获取总的的数据(总的,更新,新增)
    path("source/", views.get_source_per_data, name="source_data"),  # 每个数据的总数据量
    path("pie_sum/", views.get_source_pie_data, name="pie_data"),  # 每个数据的总数据量
    path("pie_update/", views.get_source_update_pie_data, name="pie_update_data"),  # 每个数据的更新总数据量
    path("pie_increase/", views.get_source_increase_pie_data, name="pie_increase_data"),  # 每个数据的新增总数据量
    path("bar_sum/", views.get_source_bar_data, name="bar_data"),  # 每个数据的柱状图数据量
]
