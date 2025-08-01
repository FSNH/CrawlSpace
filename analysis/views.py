import json
import logging

from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from analysis.utils.analyse import Analysis

logger_analysis = logging.getLogger('analysis_log')
analy_obj = Analysis()


# Create your views here.
@login_required(login_url='/accounts/login/')  # 设置没有登录跳转到登录页
def index(request):
    logger_analysis.info("数据统计页面请求成功!")
    return render(request, 'analysis/index.html')


@login_required(login_url='/accounts/login/')  # 设置没有登录跳转到登录页
def get_data(request):
    """
    获取总的数据量,总的更新量,总的新增量
    :param request:
    :return:
    """
    try:
        data = json.loads(analy_obj.get_all_count())
    except Exception as e:
        logger_analysis.error(e)
    else:
        # print(data)
        return JsonResponse(data)
    pass


@login_required(login_url='/accounts/login/')  # 设置没有登录跳转到登录页
def get_source_per_data(request):
    """
    获取所有数据源的总的链接数据
    :param request:
    :return:
    """
    try:
        data = json.loads(analy_obj.get_groupby_source_count())
    except Exception as e:
        logger_analysis.error(e)
    else:
        # print(data)
        return JsonResponse(data)
    pass


@login_required(login_url='/accounts/login/')  # 设置没有登录跳转到登录页
def get_source_pie_data(request):
    """
    获取所有数据数据源的饼图总占比
    :param request:
    :return:
    """
    try:
        data = json.loads(analy_obj.get_groupby_source_count())
    except Exception as e:
        logger_analysis.error(e)
    else:
        data = [[key.get("_id"), key.get("SourceCount")] for key in data.get("per_source_count")]
        # print(data)
        return JsonResponse(data, safe=False)
    pass


@login_required(login_url='/accounts/login/')  # 设置没有登录跳转到登录页
def get_source_update_pie_data(request):
    """
    获取所有数据源更新的总的占比
    """
    try:
        data = json.loads(analy_obj.get_groupby_source_update_count())
    except Exception as e:
        logger_analysis.error(e)
    else:
        data = [[key.get("_id"), key.get("SourceCount")] for key in data.get("per_source_count")]
        # print(data)
        return JsonResponse(data, safe=False)
    pass


@login_required(login_url='/accounts/login/')  # 设置没有登录跳转到登录页
def get_source_increase_pie_data(request):
    """
    获取所有数据源新增的总的占比
    """
    try:
        data = json.loads(analy_obj.get_groupby_source_increase_count())
    except Exception as e:
        logger_analysis.error(e)
    else:
        data = [[key.get("_id"), key.get("SourceCount")] for key in data.get("per_source_count")]
        # print(data)
        return JsonResponse(data, safe=False)
    pass


@login_required(login_url='/accounts/login/')  # 设置没有登录跳转到登录页
def get_source_bar_data(request):
    """
    获取每个数据的总的;新增的;更新的数据量
    :param request:
    :return:
    """

    data = []
    name_list = []
    try:

        data3 = json.loads(analy_obj.get_groupby_source_count())
        name_list = [key.get("_id") for key in data3.get("per_source_count")]  # 获取数据源
        source_sum = {list(key.values())[0]: list(key.values())[1] for key in
                      data3.get("per_source_count")}  # 数据转化成{"mce":10}
        data3 = {"name": "总的", "data": [source_sum.get(key) if source_sum.get(key) else 0 for key in
                                        name_list]}  # 转化成highchart的图标数据格式
        # print(data3)

        data1 = json.loads(analy_obj.get_groupby_source_update_count())
        update = {list(key.values())[0]: list(key.values())[1] for key in data1.get("per_source_count")}
        data1 = {"name": "更新", "data": [update.get(key) if update.get(key) else 0 for key in name_list]}
        # print(data1)

        data2 = json.loads(analy_obj.get_groupby_source_increase_count())
        increase = {list(key.values())[0]: list(key.values())[1] for key in data2.get("per_source_count")}
        data2 = {"name": "新增", "data": [increase.get(key) if increase.get(key) else 0 for key in name_list]}
        data.append(data1)
        data.append(data2)
        data.append(data3)
    except Exception as e:
        logger_analysis.error(e)
    else:
        # print(data)
        return JsonResponse([{"data": data, "name_list": name_list}], safe=False)
    pass
