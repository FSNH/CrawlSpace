import json
from pprint import pprint

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
# Create your views here.
from django.shortcuts import render
from django.forms import model_to_dict
from monitor.models import EmailInfo
from django.http.response import JsonResponse


@login_required(login_url='/accounts/login/')  # 设置没有登录跳转到登录页
def index(request):
    return render(request, "monitor/index.html")


@login_required(login_url='/accounts/login/')  # 设置没有登录跳转到登录页
def emailinfo(request):
    # 邮箱配置信息
    if request.method == "GET":
        try:
            email_infos = EmailInfo.objects.all()
            results = {}
            if email_infos:
                for info in email_infos:
                    results = model_to_dict(info)
                    results.update({"unit":info.get_unit_display(),"status":200})
                return JsonResponse(results)
            else:
                return JsonResponse({"status":400})
        except Exception as e:
            return JsonResponse({"status": 400,"message":str(e)})
    elif request.method == "POST":
        # 提交配置信息
        try:
            data = request.POST.get("data")
            if data:
                data = json.loads(data)
                objects = EmailInfo.objects.filter(email_host_pwd=data.get("email_host_pwd"))
                if objects:
                    objects.update(**data)
                    data.update({"status": 200})
                    return JsonResponse(data)
                else:
                    EmailInfo.objects.create(**data)
                    data.update({"status": 200})
                    return JsonResponse(data)
        except Exception as e:
            data = {"status": 400,"message":str(e)}
            return JsonResponse(data)
            pass

