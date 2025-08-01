import datetime
import json
import logging

import pytz
from copy import deepcopy
from django.http import JsonResponse
from django.shortcuts import render
from django.core.paginator import PageNotAnInteger, Paginator
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJob, DjangoJobExecution
from django.contrib.auth.decorators import login_required
from spider.models import TaskCron
from crontask.utils.tasksfun import *  # 导入所有的定时任务执行函数
logger_crontask = logging.getLogger('crontask_log')
scheduler = BackgroundScheduler(timezone='Asia/Shanghai')
scheduler.add_jobstore(jobstore=DjangoJobStore(), alias='default')


# map the args
args_map = {
    'cron': ['year', 'month', 'day', 'week', 'day_of_week', 'hour', 'minute', 'second', 'start_date', 'end_date',
             'timezone'],
    'interval': ['weeks', 'days', 'hours', 'minutes', 'seconds', 'start_date', 'end_date', 'timezone'],
    'date': ['run_date', 'timezone']
}
# 定时任务的参数（个数必须与前端传递的定时参数一致）
cron_params = ["host_id", "project", "name", 'year', 'month', 'day', 'week', 'day_of_week', 'hour',
               'minute', 'second']


@login_required(login_url='/accounts/login/')  # 设置没有登录跳转到登录页
def index(request):
    """
    渲染定时任务页面
    :param request:
    :return:
    """
    global queryset
    if request.method == "GET":
        spidername = request.GET.get("spidername", '')
        try:
            pindex = request.GET.get('page', 1)
        except PageNotAnInteger:
            pindex = 1
        else:
            if spidername:
                queryset = TaskCron.objects.filter(spidername=spidername)
            else:
                queryset = TaskCron.objects.all()
        paginator = Paginator(queryset, 50)  # 创建每
        # 页显示的数量实列
        page = paginator.page(pindex)  # 传递当前页的实例对象到前端
        page_nums = paginator.num_pages
        logger_crontask.info("请求成功!")
        return render(request, "crontask/task.html",
                      {"page": page, "page_nums": page_nums})


@login_required(login_url='/accounts/login/')  # 设置没有登录跳转到登录页
def cron_task(request):
    """
    支持cron的定时任务
    :param request:
    :return:
    """
    if request.method == "POST":
        trigger = request.POST.get('trigger', 'cron')  # 取触发类型参数
        # print(trigger)
        reluefile = request.POST.get('reluefile')  # 取运行规则参数
        print(reluefile)
        logger_crontask.info(f"运行规则{reluefile}")
        task_name = request.POST.get("taskfun", excute_task)  # 调用的执行定时任务的函数
        logger_crontask.info(f"执行任务的函数{task_name}")
        project_spider = eval(request.POST.get("prj"))  # 获取通用爬虫定时任务的项目名及爬虫名,eavl()转成字典对象
        print(project_spider)
        logger_crontask.info(f"定时爬虫的名称{project_spider}")
        cron_kwargs = request.POST.get("cron_kwargs", {})  # 调用的执行定时任务的函数
        logger_crontask.info(f"定时任务的参数{cron_kwargs}")
        # print(eval(cron_kwargs) if isinstance(cron_kwargs, str) else cron_kwargs)
        data = request.POST.get("data")
        print(data)
        if data:
            data = json.loads(data)
            logger_crontask.info(f"定时任务获取的前端数据参数:{data}")
            params_dict = {k: v for k, v in zip(cron_params, data)}
            configurations = {arg: params_dict.get(arg, "") for arg in args_map[trigger] if
                              params_dict.get(arg, "") != ""}
            # print(configurations)
            logger_crontask.info(f"定时任务创建的配置参数:{configurations}")
            try:
                """
                id可以不加,如果不加ID是这个应用view下的函数名字
                replace_existing=True 这个东西不加的话，他会提示ID冲突了,我查了好多文章，把这答案找出来了 。
                """
                scheduler.add_job(
                    jobstore='default',
                    func=eval(task_name),  # 函数不能加引号，否则报错：无效引用,使用eval()将字符串转成function类型
                    trigger="cron",  # 默认cron模式
                    args=[reluefile],
                    kwargs=eval(cron_kwargs) if isinstance(cron_kwargs, str) else cron_kwargs,
                    replace_existing=True,
                    id=reluefile if reluefile else project_spider.get('spidername'),  # id为django jobs模型的id
                    **configurations
                )
                # print(sche)
                configurations.update({"trigger": "cron"})  # 定时任务配置信息添加触发字段
                configurations.update({"client_id": eval(cron_kwargs).get("client_id")})  # 定时任务配置信息添加主机id字段
                # print(str(configurations))
                try:
                    # 爬虫名称+规则名称判断任务是否已经创建
                    TaskCron.objects.get(spidername=project_spider.get('spidername'), rulefile=reluefile)
                except TaskCron.DoesNotExist:
                    logger_crontask.error("定时任务不存在!")
                else:
                    logger_crontask.warning("定时任务已经存在")
                    return JsonResponse({"status": 400, "message": "定时任务已经存在"})
            except Exception as e:
                # print(e)
                logger_crontask.error(e)
                return JsonResponse({"status": 400, "message": str(e)})
            else:
                if not scheduler.running:
                    logger_crontask.info("任务运行!")
                    scheduler.start()
                # 定时任务不存在就新建任务到taskcron
                if reluefile:
                    job = DjangoJob.objects.get(id=reluefile)  # DjangoJob的实例
                else:
                    job = DjangoJob.objects.get(id=project_spider.get('spidername'))  # DjangoJob的实例
                TaskCron.objects.create(project=project_spider.get('project'),
                                        spidername=project_spider.get('spidername'),
                                        rulefile=reluefile,
                                        configuration=str(configurations),
                                        job=job
                                        )
                logger_crontask.info("定时任务创建成功!")
                return JsonResponse({"status": 200, "message": "创建成功"})
    else:
        logger_crontask.info("定时任务创建失败!")
        return JsonResponse({"status": 400, "message": "创建失败，缺少参数"})


@login_required(login_url='/accounts/login/')  # 设置没有登录跳转到登录页
def taskinfo(request):
    """
    获取定时任务的状态及下次运行时间任务列表
    :param request:
    :return: json
    """
    if request.method == "POST":
        data = request.POST.get("data")
        if data:
            results = []
            for jobid in eval(data):
                # print(jobid)
                # 初始化返回参数
                result = {"project": "", "spidername": "", "rulefile": jobid,
                          "run_time": "",
                          "finished_time": "",
                          "state": "准备中",  # 默认状态为准备中
                          "success_count": "",
                          "failure_count": ""
                          }
                jobs = DjangoJobExecution.objects.filter(job_id=jobid)
                res_task = DjangoJobExecution.objects.values_list("job_id", "status")
                if res_task and jobs:
                    t = jobs.first()
                    group_by_value = {}
                    for val, s in res_task:  # 按照jobid
                        group_by_value[val] = [value for value in DjangoJobExecution.objects.filter(job_id=jobid) if
                                               value.status == "Executed"]  # 成功次数
                    # print(group_by_value)
                    success_count = len(group_by_value.get(t.job_id)) if group_by_value.get(t.job_id) else 0  # 成功次数
                    failure_count = len(jobs.values_list("status")) - success_count  # 失败次数
                    # print(failure_count)

                    finished_time = datetime.datetime.fromtimestamp(int(t.finished),
                                                                    pytz.timezone('Asia/Shanghai')).strftime(
                        '%Y-%m-%d %H:%M:%S')
                    result.update({"run_time": datetime.datetime.strftime(t.run_time + datetime.timedelta(hours=8),
                                                                          "%Y年%m月%d日 %H:%M:%S") if t.run_time else "",
                                   "finished_time": finished_time if finished_time else "",
                                   "state": t.exception,
                                   "success_count": success_count if success_count else "",
                                   "failure_count": failure_count})
                results.append(result)
            # print(results)
            logger_crontask.info(f'任务信息:{results}')
            return JsonResponse({"results": results, "status": 200}, safe=False)
        logger_crontask.info("参数为空!")
        return JsonResponse({"msg": "参数为空", "status": 400}, safe=False)


@login_required(login_url='/accounts/login/')  # 设置没有登录跳转到登录页
def deltask(request):
    """
    单个及批量删除定时任务
    :param request:
    :return:
    接受参数：rulename:rulename;rulename:spider
    """
    if request.method == "POST":
        jobids = request.POST.get("data")  # 批量删除
        if jobids:
            jobids = eval(jobids)  # 字符串还原list
            for jobid in jobids:
                id = jobid.split(':')[0]
                DjangoJobExecution.objects.filter(job_id=id).delete()
                if jobid.split(':')[1] == 'spider':  # 如果传递过来的参数包含spider
                    TaskCron.objects.get(spidername=id).delete()
                else:
                    TaskCron.objects.get(rulefile=id).delete()
                DjangoJob.objects.get(id=id).delete()
                # scheduler.remove_job(job_id=jobid)
            logger_crontask.info(f"删除任务成功:{jobids}")
            return JsonResponse({"status": 200, "count": len(jobids)})
        else:
            logger_crontask.warning("参数为空!")
            return JsonResponse({"status": 400, "msg": "参数数据为空"})
    elif request.method == "GET":
        jobid = request.GET.get("data")  # 单个删除
        id = jobid.split(':')[0]
        try:
            DjangoJobExecution.objects.filter(job_id=id).delete()
            if jobid.split(':')[1] == 'spider':  # 如果传递过来的参数包含spider
                TaskCron.objects.get(spidername=id).delete()
            else:
                TaskCron.objects.get(rulefile=id).delete()
            DjangoJob.objects.get(id=id).delete()
            # scheduler.remove_job(job_id=jobid)
        except Exception as e:
            logger_crontask.error(e)
            return JsonResponse({"status": 400, "msg": f"{e}"})
        else:
            logger_crontask.info(f"单个任务删除成功:{jobid}")
            return JsonResponse({"status": 200})


@login_required(login_url='/accounts/login/')  # 设置没有登录跳转到登录页
def croninfo(request, rulename):
    """
    获取任务的配置信息
    :param request:
    :param rulename:
    :return:
    """
    result = {}
    try:
        if rulename.split(':')[1] == 'spider':
            cron_info = TaskCron.objects.get(spidername=rulename.split(':')[0])
        else:
            cron_info = TaskCron.objects.get(rulefile=rulename.split(':')[0])
        # print(cron_info)
    except TaskCron.DoesNotExist:
        result.update({"configuation": ""})
        logger_crontask.error("数据不存在!")
        return JsonResponse({"status": 400, "msg": "数据不存在"}, safe=False)
    else:
        logger_crontask.info(f"配置信息获取成功!-{cron_info.configuration}")
        result.update({"configuation": eval(cron_info.configuration), "status": 200})
    return JsonResponse(result, safe=False)


@login_required(login_url='/accounts/login/')  # 设置没有登录跳转到登录页
def cancel_cron(request, rulename):
    """
    暂停定时任务
    :param rulename:
    :param request:
    :return:
    """
    # print(rulename)
    rulename = rulename.split(":")[0]
    try:
        scheduler.pause_job(job_id=rulename, jobstore='default')
    except Exception as e:
        logger_crontask.error(e)
        return JsonResponse({"status": 400, "msg": f"{e}"})
    else:
        logger_crontask.info(f"取消任务成功-{rulename}")
        return JsonResponse({"status": 200})


@login_required(login_url='/accounts/login/')  # 设置没有登录跳转到登录页
def restart_cron(request, rulename):
    """
    重启定时任务
    :param rulename:
    :param request:
    :return:
    """
    rulename = rulename.split(":")[0]
    print(rulename)
    print(scheduler.get_jobs(jobstore='default'))
    try:
        print("222")
        scheduler.resume_job(job_id=rulename, jobstore='default')
    except Exception as e:
        logger_crontask.error(e)
        return JsonResponse({"status": 400, "msg": f"{e}"})
    else:
        logger_crontask.info(f"重启任务成功-{rulename}")
        return JsonResponse({"status": 200})


# TODO：任务视图待处理
@login_required(login_url='/accounts/login/')  # 设置没有登录跳转到登录页
def jobinfo(request, rulename):
    results = scheduler.get_jobs()
    # print(results)
    return JsonResponse(results)


@login_required(login_url='/accounts/login/')  # 设置没有登录跳转到登录页
def re_sche(request, rulename):
    """重新调度(程序更新或重启后)"""
    job_id = ""
    task_name = ''
    if rulename.split(':')[1] == 'spider':
        job_id = rulename.split(':')[0]
        task_name = "excute_spider"
        task_cron = TaskCron.objects.get(spidername=rulename.split(':')[0])
    else:
        job_id = rulename.split(':')[0]
        job_id = job_id + ".json" if "json" not in job_id else job_id
        task_name = "excute_task"
        task_cron = TaskCron.objects.get(rulefile=rulename.split(':')[0])
    # print(task_cron)
    if task_cron:
        configurations = task_cron.configuration
        configurations = eval(configurations)
        configurations_copy = deepcopy(configurations)
        # print(job_id, task_name)
        cron_params = {"project": task_cron.project, "name": job_id, "client_id": configurations_copy.get("client_id")}
        configurations.pop("client_id")
        configurations.pop("trigger")
        try:
            scheduler.add_job(
                jobstore='default',
                func=eval(task_name),  # 函数不能加引号，否则报错：无效引用,使用eval()将字符串转成function类型
                trigger="cron",  # 默认cron模式
                args=[rulename],
                kwargs=cron_params,
                replace_existing=True,
                id=job_id,  # id为django jobs模型的id
                **configurations
            )
        except Exception as e:
            logger_crontask.error(e)
            return JsonResponse({"status": 400, "message": str(e)})
        else:
            if not scheduler.running:
                logger_crontask.info("任务运行!")
                scheduler.start()
            logger_crontask.info("定时任务重新调度成功!")
            return JsonResponse({"status": 200, "message": "调度成功"})



