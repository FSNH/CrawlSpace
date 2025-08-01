import json
import logging
import time
import traceback
import zipfile
import django
import pytz
import requests
from django.core.paginator import PageNotAnInteger, Paginator
from django.forms import model_to_dict
from django.shortcuts import render
from django.http.response import JsonResponse, HttpResponse
import shutil
import os
from os.path import join
from spider.models import TaskStatusList, Client, Deploy, Project,PackagePath
from datetime import datetime
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from spider.utils.build import build_project, find_egg
from spider.utils.get_tree import get_tree
from spider.utils.scrapydconf import ScrapydConf, scrapyd_url, get_scrapyd, get_node_info
from spider.utils.parsellog import LogparserScrapyLog
from CrawlSpace.settings import PROJECTS_FOLDER, TIME_ZONE, EDIT_FOLDER
from spider.utils.get_egg_list import del_file_paths
from spider.utils.packagepath import PackPath

logger = logging.getLogger('django')
logger_spider = logging.getLogger('spider_log')
IGNORES = ['.git/', '*.pyc', '.DS_Store', '.idea/',
           '*.egg', '*.egg-info/', '*.egg-info', 'build/', 'log']

scrapydconf = ScrapydConf()  # 初始化通用爬虫信息
logparser = LogparserScrapyLog()

import pdb


# Create your views here.
@login_required(login_url='/accounts/login/')  # 设置没有登录跳转到登录页
def server(request):
    """主机首页"""
    global queryset
    if request.method == "GET":
        hostname = request.GET.get("hostname", '')
        # print(hostname)
        try:
            pindex = request.GET.get('page', 1)
        except PageNotAnInteger:
            pindex = 1
        else:
            if hostname:
                queryset = Client.objects.filter(name=hostname)
            else:
                queryset = Client.objects.all().order_by('-id')
        paginator = Paginator(queryset, 50)  # 创建每页显示的数量实列
        page = paginator.page(pindex)  # 传递当前页的实例对象到前端
        page_nums = paginator.num_pages
        return render(request, "spider/server.html", {"page": page, "page_nums": page_nums})
    elif request.method == 'POST':
        # 获取主机的信息
        client_id = request.POST.get("client_id")
        try:
            client = Client.objects.filter(id=client_id).first()
            client_info = model_to_dict(client)
            client_info.update({"status": 200})
        except Exception as e:
            logger_spider.error(e)
            logger.error(e)
            # print(e)
        else:
            logger_spider.info(f"主机基本信息加载成功:{client_info}")
            logger.info(f"主机基本信息加载成功:{client_info}")
            return JsonResponse(client_info)


@login_required(login_url='/accounts/login/')  # 设置没有登录跳转到登录页
def client_status(request):
    """
    获取主机的状态
    :param request: request object
    :param client_id: client id
    :return: json
    """
    if request.method == 'GET':
        # get client object
        results = []
        data = request.GET.get("data")
        for client_id in json.loads(data):
            try:
                client = Client.objects.get(id=client_id)
                requests.get(scrapyd_url(client.ip, client.port), timeout=3)
            except Exception as e:
                logger.error(e)

                results.append(400)
            else:
                results.append(200)
        logger.info(f"主机状态信息如下:{results}")
        return JsonResponse({'status': 200, 'results': results})


@login_required(login_url='/accounts/login/')  # 设置没有登录跳转到登录页
def client_create(request):
    """
    创建客户端
    :param request: request object
    :return: json
    """
    if request.method == 'POST':
        try:
            ID = request.POST.get("ID")
            data = {
                "name": request.POST.get("name"),
                "ip": request.POST.get("ip"),
                "port": request.POST.get("port"),
                "auth": request.POST.get("auth"),
                "username": request.POST.get("username"),
                "password": request.POST.get("password"),
                "client_enable":request.POST.get("client_enable")
            }
            # print(data)
            if Client.objects.filter(id=ID).first():
                Client.objects.filter(id=ID).update(**data)
                return JsonResponse({"status": 300}, safe=False)
            Client.objects.create(**data)
        except Exception as e:
            # print(e)
            logger.error(e)
            logger_spider.error(e)
            return JsonResponse({"status": 400, "msg": str(e)}, safe=False)
        logger.info(f"{ID}:主机创建成功!-{data}")
        return JsonResponse({"status": 200}, safe=False)


@login_required(login_url='/accounts/login/')  # 设置没有登录跳转到登录页
def client_remove(request, client_id):
    """
    删除主机
    :param request: request object
    :param client_id: client id
    :return: json
    """
    if request.method == 'GET':
        try:
            client = Client.objects.get(id=client_id)
            # delete deploy
            Deploy.objects.filter(client=client).delete()
            # delete client
            Client.objects.filter(id=client_id).delete()
        except Exception as e:
            logger.error(e)
            logger_spider.error(e)
            return JsonResponse({'status': 400, "msg": str(e)})
        logger.info(f"{client_id}:主机删除成功!")
        return JsonResponse({'status': 200})


@login_required(login_url='/accounts/login/')  # 设置没有登录跳转到登录页
def deploy(request):
    """
    部署页首页
    :param request:
    :return:
    """
    """
       上传scrapy项目到服务器,仅支持压缩包
    """

    if request.method == "GET":

        packs=[]
        for pack in PackagePath.objects.all():
            packs.append({"name":pack.name,"path":pack.path})
        clients = []
        for client in Client.objects.all():
            ip_port = "[" + str(client.id) + "]" + client.ip + ":" + str(client.port)
            clients.append({"host": ip_port})
            logger.info(ip_port)
        # logger.info(f"成功获取到可以部署的项目{projects}")
        return render(request, "spider/deploy.html",
                      { "clients": clients, "project_count": len(packs),
                       "client_count": len(clients), "packs":packs,"status": 200, "message": "请至少选择一个文件包"})
    else:
        pass

# @login_required(login_url='/accounts/login/')  # 设置没有登录跳转到登录页
def packs_projects(request,pro_path):
    """
    根据仓库路径获取爬虫项目
    :param request:
    :return:
    """
    if request.method == "GET":
        try:
            path = os.path.abspath(join(os.getcwd(), PROJECTS_FOLDER))
            print(path)
            cpath = join(path,pro_path)
            print(cpath)
            projects = []
            files = os.listdir(cpath)
            files.sort(key=lambda x: x.lower()[:4])  # 排序sort()在原可迭代对象上处理，sorted()新建一个空间
            for file in files:
                if os.path.isdir(join(cpath, file)) and not file in IGNORES:
                    projects.append({'name': file})
        except Exception as e:
            return JsonResponse({'msg': str(e), 'status': 500})

        return JsonResponse({'msg': '成功',"projects":projects, 'status': 200,"project_count": len(projects)})


@login_required(login_url='/accounts/login/')  # 设置没有登录跳转到登录页
def client_project(request):
    """
    渲染主机部署的项目
    :param request:
    :param client_id:主机id
    :return: json
    """
    global projects
    if request.method == "GET":
        client_id = request.GET.get("client_id")
        try:
            # 直接获取scrapyd部署的项目
            # client = Client.objects.get(id=client_id)
            # scrapyd = get_scrapyd(client=client)
            # project = scrapyd.list_projects()
            # projects = []
            # for p in project:
            #     projects.append({"name": p, "client_id": client_id})
            # print(projects)
            # 从数据库中获取部署的项目
            deploys = Deploy.objects.filter(client_id=client_id)
            projects = []
            for deploy in deploys:
                model = Project.objects.filter(id=deploy.project_id)
                print(model)
                for pro in model:
                    pack = PackagePath.objects.get(path=pro.package)
                    projects.append({"name": pro.name, "client_id": client_id,"package":pro.package,"cname":pack.name})
                    logger.info(f"获取待scrapy项目:{pro}")
        except Exception as e:
            logger.error(e)
            logger_spider.error(e)
            return JsonResponse({"msg": str(e), "status": 400}, safe=False)
    elif request.method == "POST":
        client_id = request.GET.get("client_id")
        project_name_list = request.POST.get("formdata", '')  # 筛选出多个项目并重新启动
        try:
            deploys = Deploy.objects.filter(client_id=client_id)
            projects = []
            for deploy in deploys:
                if project_name_list:
                    logger.info(f"批量运行scrapy项目:{project_name_list}")
                    for project_name in json.loads(project_name_list):
                        model = Project.objects.filter(id=deploy.project_id, name=project_name)
                        for pro in model:
                            pack = PackagePath.objects.get(path=pro.package)
                            projects.append({"name": pro.name, "client_id": client_id,"package":pro.package,"cname":pack.name})
                else:
                    model = Project.objects.filter(id=deploy.project_id)
                    for pro in model:
                        pack = PackagePath.objects.get(path=pro.package)
                        projects.append({"name": pro.name, "client_id": client_id, "package": pro.package, "cname": pack.name})
        except Exception as e:
            logger.error(e)
            logger_spider.error(e)
            return JsonResponse({"msg": str(e), "status": 400}, safe=False)
    logger.info(f"当前项目:{projects}")
    return render(request, 'spider/scheduler.html', {"data": projects, "status": 200})


@login_required(login_url='/accounts/login/')  # 设置没有登录跳转到登录页
def project_deploy(request, client_id, project_name,cpath):
    """
    部署项目到主机
    :param request: request object
    :param client_id: client id
    :param project_name: project name
    :return: json of deploy result
    """
    if request.method == 'POST':
        try:
            # get project folder

            path = os.path.abspath(join(os.getcwd(), PROJECTS_FOLDER))
            projectpath = join(path, cpath)
            project_path=join(projectpath,project_name)
            # get egg filename
            data = json.loads(request.POST.get("data"))
            egg = data.get("egg")
            if not egg:
                logger.warning('egg not found')
                return JsonResponse({'msg': 'egg not found', 'status': 500})
            egg_file = open(join(project_path, egg), 'rb')
            # print(egg_file)
            # get client and project model
            client = Client.objects.get(id=client_id)
            project = Project.objects.get(name=project_name,package=cpath)
            # execute deploy operation
            scrapyd = get_scrapyd(client)
            # pdb.set_trace()
            scrapyd.add_version(project_name, int(time.time()), egg_file.read())
            # update deploy info
            deployed_at = timezone.now()
            Deploy.objects.filter(client=client, project=project).delete()
            deploy, result = Deploy.objects.update_or_create(client=client, project=project, deployed_at=deployed_at,
                                                             description=project.description)
            data = model_to_dict(deploy)
            data.update({"status": 200})
        except Exception as e:
            logger_spider.error(e)
            logger.error(e)
            return JsonResponse({"status": 400, "msg": str(e)}, safe=False)
        else:
            logger_spider.info(f"{project_name}:项目部署{client_id}:号机成功")
            logger.info(f"{project_name}:项目部署{client_id}:号机成功")
            return JsonResponse(data)


@login_required(login_url='/accounts/login/')  # 设置没有登录跳转到登录页
def project_build(request, project_name,cpath):
    """
    GET获取打包的信息
    POST执行打包的操作
    :param request: request object
    :param project_name: project name
    :return: json
    """
    # 获取项目所在的自定义的项目目录PROJECTS_FOLDER
    path = os.path.abspath(join(os.getcwd(), PROJECTS_FOLDER))
    project_path = join(path, cpath)
    pro_path = join(project_path,project_name)
    # 获取项目部署的版本信息
    if request.method == 'GET':
        egg_list = find_egg(pro_path)
        from copy import deepcopy
        egg = deepcopy(egg_list)[0] if egg_list else ""

        # 如果打包了项目，保存或者更新打包版本项目到数据库Project
        if egg:
            built_at = timezone.datetime.fromtimestamp(os.path.getmtime(join(pro_path, egg)),
                                                       tz=pytz.timezone(TIME_ZONE))
            if not Project.objects.filter(name=project_name,package=cpath):
                Project(name=project_name, built_at=built_at, egg=egg,package=cpath).save()
                model = Project.objects.get(name=project_name,package=cpath)
            else:
                model = Project.objects.get(name=project_name,package=cpath)
                model.built_at = built_at
                model.egg = egg_list
                model.package=cpath
                model.save()
        # 如果项目没有被打包，仅仅保存项目名称到数据库Project
        else:
            if not Project.objects.filter(name=project_name,package=cpath):
                Project(name=project_name,package=cpath).save()
            model = Project.objects.get(name=project_name,package=cpath)
        # transfer model to dict then dumps it to json
        data = model_to_dict(model)
        clients = []
        # 获取项目对应的部署主机
        for client in data.get("clients"):
            clients.append(client.id)
        # print(data)
        data.update({"egg":eval(data.get("egg"))}) if isinstance(data.get("egg"),str) else data
        data.update({"clients": json.dumps(clients)})
        logger.info(f"获取当前的部署主机:{clients}")
        return JsonResponse(data)

    # build operation manually by clicking button
    elif request.method == 'POST':
        try:
            data = json.loads(request.POST.get("data"))
            # print(project_name)
            description = data['description']
            version = data.get("version", 1.0)
            build_project(cpath+"/"+project_name, version)
            egg = find_egg(pro_path)
            if not egg:
                logger.info('egg not found')
                return JsonResponse({'message': 'egg not found'}, status=500)
            # update built_at info
            built_at = timezone.now()
            # if project does not exists in db, create it
            if not Project.objects.filter(name=project_name,package=cpath):
                Project(name=project_name, description=description,
                        built_at=built_at, egg=egg, version=version,package=cpath).save()
                model = Project.objects.get(name=project_name,package=cpath)
            # if project exists, update egg, description, built_at info
            else:
                model = Project.objects.get(name=project_name,package=cpath)
                model.built_at = built_at
                model.egg = egg
                model.description = description
                model.version = version
                model.package=cpath
                model.save()
            # transfer model to dict then dumps it to json
            data = model_to_dict(model)
            clients = []
            # 获取项目对应的部署主机
            # TODO:TypeError: Object of type Client is not JSON serializable
            for client in data.get("clients"):
                clients.append(client.id)
            data.update({"clients": json.dumps(clients), "version": version})
            data.update({"status": 200})
            # print(data)
            logger.info(f"{project_name}:项目打包成功")
        except Exception as e:
            traceback.print_exc()

        return JsonResponse(data)


@login_required(login_url='/accounts/login/')  # 设置没有登录跳转到登录页
def project_upload(request):
    """
    上传scrapy项目到服务器项目路径,仅支持压缩包
    """
    # 获取项目所在的自定义的项目目录PROJECTS_FOLDER
    path = os.path.abspath(join(os.getcwd(), PROJECTS_FOLDER))
    if request.method == 'POST' and request.FILES.getlist('files[]'):
        ppath = request.POST.get("propath")
        if ppath and ppath!="选择项目仓库":
            # print(request.FILES.getlist('files[]'))
            cpath = join(path,request.POST.get("propath"))
            extract_folders = []
            for name in request.FILES.getlist('files[]'):
                # print(name)
                try:
                    zip_file = name
                    extract_folder = zip_file.name.split('.')[0]  # 获取不带后缀名压缩包文件名
                    # print(extract_folder)
                    # 思路一：将文件解压出来并遍历目录下的文件（带文件路径）
                    if zip_file.name.split(".")[-1] in ["zip"]:
                        zip_file = zipfile.ZipFile(zip_file)
                        # print(zip_file)
                        # 将文件解压到文件夹
                        zip_file.extractall(path=cpath)
                        zip_file.close()  # 关闭
                    else:
                        return JsonResponse({"status": 400, "folder_path": "", "message": "不支持的文件格式！"})
                except Exception as e:
                    return JsonResponse({"status": 400, "folder_path": "", "message": str(e)})
                else:
                    extract_folders.append(extract_folder)
            return JsonResponse(
                {"status": 200,
                 "folder_path": "<br/>".join([path +"/"+ppath+ '/' + extract_folder for extract_folder in extract_folders]),
                 "message": "上传成功"})
        else:
            return JsonResponse(
                {"status": 200,
                 "folder_path": "",
                 "message": "请至少选择一个文件压缩包以及一个项目仓库"})
    else:
        packs = []
        for pack in PackagePath.objects.all():
            packs.append({"name": pack.name, "path": pack.path})
        return render(request, "spider/upload.html", {"status": 200, "message": "请至少选择一个文件压缩包以及一个项目仓库","packs":packs})


@login_required(login_url='/accounts/login/')  # 设置没有登录跳转到登录页
def spider_list(request, client_id):
    """
    从scrapyd获取爬虫列表
    :param request: request Object
    :param client_id: client id
    :return: jsons
    """
    if request.method == "POST":
        data = request.POST.get("data")
        spiders_list = []
        try:
            client = Client.objects.get(id=client_id)
            scrapyd = get_scrapyd(client)
            for project_name in eval(data):
                spiders = scrapyd.list_spiders(project_name)
                spiders = [{'name': spider, 'id': index + 1, "project_name": project_name}
                           for index, spider in enumerate(spiders)]
                spiders_list.append(spiders)
                # print(spiders_list)
                logger.info(spider_list)
        except Exception as e:
            logger.error(e)
            return JsonResponse({"status": 400, "msg": str(e)}, safe=False)
        # print(spiders_list)
        logger.info(f"获取到的爬虫的列表{spiders_list}")
        return JsonResponse({"spiders": spiders_list, "status": 200, "count": len(spiders_list)}, safe=False)


@login_required(login_url='/accounts/login/')  # 设置没有登录跳转到登录页
def spider_start(request, client_id,cpath):
    """
    运行一个爬虫
    :param request: request object
    :param client_id: client id
    :param project_name: project name
    :param spider_name: spider name
    :return: json
    """
    if request.method == 'POST':
        try:
            data = request.POST.get("data")
            client = Client.objects.get(id=client_id)
            scrapyd = get_scrapyd(client)
            job_list = []
            for spider in eval(data):
                # print(spider.get('project_name'), spider.get('spider_name'))
                job = scrapyd.schedule(spider.get('project_name'), spider.get('spider_name'))
                # print(job)
                job_list.append(job)
                TaskStatusList.objects.create(project=spider.get('project_name'), spidername=spider.get('spider_name'),
                                              rulefile='', jobid=job, client=client,package=cpath)
        except Exception as e:
            logger.error(e)
            logger_spider.error(e)
            return JsonResponse({'msg': str(e), "status": 400})
        # print(job_list)
        logger.info(f"运行成功的项目id{job_list}")
        return JsonResponse({'count': len(job_list), "jobs": job_list, "status": 200})


@login_required(login_url='/accounts/login/')  # 设置没有登录跳转到登录页
def del_project(request, client_id,cpath):
    """
    批量删除部署在服务器上的项目
    :param request:
    :param client_id: 主机号
    :return:
    """
    try:
        project_list = request.GET.get("project_list")
        # print(project_list)
        client = Client.objects.get(id=client_id)
        scrapyd = get_scrapyd(client)
        results = []  # 删除成功的项目
        for pro in json.loads(project_list):
            # 判断删除的项目是否存在运行的爬虫任务job,存在就取消
            spder_jobs = scrapyd.list_jobs(project=pro.get("project_name"))
            # print(spder_jobs.get("running"))
            if spder_jobs.get("running"):
                for job in spder_jobs.get("running"):  # 获取运行的任务
                    scrapyd.cancel(project=pro.get("project_name"), job=job.get("id"))  # 取消正在运行的任务
            res = scrapyd.delete_project(project=pro.get("project_name"))  # 然后再删除任务
            # print(res)
            if res:
                project = Project.objects.get(name=pro.get("project_name"),package=cpath)  # 获取project表的项目id
                Deploy.objects.filter(client_id=client_id, project_id=project.id).delete()  # 删除部署表的数据
                TaskStatusList.objects.filter(project=pro.get("project_name"),package=cpath).delete()  # 删除任务队列中的数据
                results.append({"project_name": pro})
            else:
                pass
    except Exception as e:
        logger.error(e)
        return JsonResponse({"msg": str(e), 'status': 400})
    else:
        # projects = Project.objects.values_list(id)  # 获取project表的所有项目id
        # for project_id in projects:  # 如果项目没有被部署到主机就从项目中删除
        #     if Deploy.objects.filter(project_id=project_id):
        #         pass
        #     else:
        #         Deploy.objects.filter(project_id=project_id).delete()
        logger.info(results)
        return JsonResponse({"results": results, "count": len(results), 'status': 200})


@login_required(login_url='/accounts/login/')  # 设置没有登录跳转到登录页
def project_code(request,package, project_name):
    """
    get渲染页面
    post获取当前的文件的源代码
    :param project_name:
    :param request:
    :return:
    """
    if request.method == "POST":
        path = request.POST.get("path")
        print(path)
        mode = request.POST.get("mode")
        if mode == "get":  # 如果参数mode为get就获取文件的内容
            try:
                if os.path.exists(os.path.join(path, project_name)):
                    with open(os.path.join(path, project_name), "r+", encoding='utf-8') as f:
                        codes = f.readlines()
                    return JsonResponse({"code": "".join(codes), "status": 200})
                else:
                    logger.error("文件不存在")
                    return JsonResponse({"msg": "文件不存在", "status": 400})
            except IsADirectoryError:  # 点击的文件夹不做处理
                logger.error("点击了文件夹，需要点击下拉标志！")
                pass
        elif mode == 'save':  # 如果参数mode为save就保存接受到内容到指定的文件
            source_code = request.POST.get("source_code")
            # print(path,mode,source_code)
            try:
                if os.path.exists(os.path.join(path, project_name)):
                    # 写入修改后的代码到文件中
                    with open(os.path.join(path, project_name), "w+", encoding='utf-8') as f:
                        f.write(source_code)
                    return JsonResponse({"status": 200})
                else:
                    logger.error("文件不存在")
                    return JsonResponse({"msg": "文件不存在", "status": 400})
            except IsADirectoryError:  # 点击的文件夹不做处理
                logger.error("点击了文件夹，需要点击下拉标志！")
                pass

    return render(request, 'spider/code.html')


@login_required(login_url='/accounts/login/')  # 设置没有登录跳转到登录页
def project_tree(request, package,project_name):
    """
    get file tree of project
    :param request: request object
    :param project_name: project name
    :return: json of tree
    """
    if request.method == 'GET':
        path = os.path.abspath(join(os.getcwd(), PROJECTS_FOLDER))
        # get tree data
        logger.info(path)
        tree = get_tree(join(path, package+"/"+project_name))
        # print(tree)
        logger.info(tree)
        return JsonResponse(tree, safe=False)


# 以上为项目打包编辑查看部署部分
#  -------------------------------------------------
@login_required(login_url='/accounts/login/')  # 设置没有登录跳转到登录页
def node_state(request):
    """
    获取节点的运行状态
    :param request:
    :return: json
    """
    node_infos = []
    try:
        clients = Client.objects.all()
        for client in clients:
            try:
                scrapyd = get_scrapyd(client)
                projects_count = len(scrapyd.list_projects())
            except Exception as e:
                logger.error(e)
                logger.error("projects_count设置为0")
                projects_count = 0
            node_info = get_node_info(client)
            node_info.update({"client_id": client.name, "projects_count": projects_count,
                              "update_time": time.strftime('%Y-%m-%d %H:%M:%S')})
            node_infos.append(node_info)
    except Exception as e:
        logger.error(e)
        return JsonResponse({"status": 400, "result": str(e)})
    else:
        # print(node_infos)
        logger.info(f"主机节点状态信息:{node_infos}")
        return JsonResponse(node_infos, safe=False)


@login_required(login_url='/accounts/login/')  # 设置没有登录跳转到登录页
def node(request):
    """
    节点数据可视化
    :param request:
    :return:
    """
    return render(request, 'spider/states.html')


@login_required(login_url='/accounts/login/')  # 设置没有登录跳转到登录页
def task_list(request):
    """
    任务列表页面
    :param request:
    :return:
    """
    global queryset
    global clients
    global host_id
    if request.method == "GET":
        spidername = request.GET.get("spidername", '')  # 任务
        host_id = request.GET.get("host_id", '')  # 主机号
        host_id = host_id if host_id else ''
        try:
            pindex = request.GET.get('page', 1)
        except PageNotAnInteger:
            pindex = 1
        else:
            if spidername and host_id:
                queryset = TaskStatusList.objects.filter(client_id=host_id, spidername__contains=spidername)
            elif host_id:
                queryset = TaskStatusList.objects.filter(client_id=host_id)
            elif spidername:
                queryset = TaskStatusList.objects.filter(spidername__contains=spidername)
            else:
                queryset = TaskStatusList.objects.all().order_by('-id')
        client_lsit = []
        clients = Client.objects.all()
        for client in clients:
            ip_port = "[" + str(client.id) + "]" + client.ip + ":" + str(client.port)
            client_lsit.append({"host": ip_port, "id": client.id})
        paginator = Paginator(queryset, 20)  # 创建每页显示的数量实列
        try:
            page = paginator.page(pindex)  # 传递当前页的实例对象到前端
        except django.core.paginator.EmptyPage:
            # 翻页不存在
            return render(request, "spider/task.html",
                          {"page": "", "page_nums": 0, "clients": client_lsit, "host_id": host_id})
        else:
            page_nums = paginator.num_pages
            logger.info(host_id)
            logger.info(page_nums)
            logger.info(clients)
            return render(request, "spider/task.html",
                          {"page": page, "page_nums": page_nums, "clients": client_lsit, "host_id": host_id})
    else:
        return HttpResponse("不支持POST请求")


@login_required(login_url='/accounts/login/')  # 设置没有登录跳转到登录页
def task_log(request, project, spider, jobid):
    """
    浏览任务日志
    :param spider:
    :param request:
    :param project:
    :param jobid:
    :return:
    """
    client_id = request.GET.get("client_id")
    client = Client.objects.filter(id=client_id).first()
    url = scrapyd_url(ip=client.ip, port=client.port)
    # print(url)
    view_log_url = f"{url}/logs/{project}/{spider}/{jobid}.log"
    logger.info(view_log_url)
    return JsonResponse({"view_log_url": view_log_url, "status": 200})


@login_required(login_url='/accounts/login/')  # 设置没有登录跳转到登录页
def job_log(request, client_id, project_name, spider_name, job_id):
    """
    获取日志文件的日志
    :param request: request object
    :param client_id: client id
    :param project_name: project name
    :param spider_name: spider name
    :param job_id: job id
    :return: log of job
    """
    if request.method == 'GET':
        client = Client.objects.get(id=client_id)
        # get log url
        url = scrapyd_url(ip=client.ip, port=client.port)
        # print(url)
        view_log_url = f"{url}/logs/{project_name}/{spider_name}/{job_id}.log"
        # print(view_log_url)
        # get last 1000 bytes of log
        response = requests.get(url=view_log_url, timeout=5, headers={
            'Range': 'bytes=-1000'
        }, auth=(client.username, client.password) if client.auth else None)
        # Get encoding
        encoding = response.apparent_encoding
        # log not found
        if response.status_code == 404:
            return JsonResponse({'message': 'Log Not Found'}, status=404)
        # bytes to string
        text = response.content.decode(encoding, errors='replace')
        # print(text)
        return HttpResponse(text)


@login_required(login_url='/accounts/login/')  # 设置没有登录跳转到登录页
def states_log(request):
    """
    日志解析结果页面
    :param request:
    :return:
    """
    return render(request, 'spider/states.html')


@login_required(login_url='/accounts/login/')  # 设置没有登录跳转到登录页
def states(request, project, spidername, jobid):
    """
    查看日志 解析的结果
    :param jobid: 任务id
    :param project: 项目
    :param spidername: 爬虫名
    :param request:
    :return: json
    """
    if request.method == "GET":
        client_id = request.GET.get("client_id")
        client = Client.objects.filter(id=client_id).first()
        url = scrapyd_url(ip=client.ip, port=client.port)
        # print(url)
        view_log_url = f"{url}/logs/{project}/{spidername}/{jobid}.log"
        # print(view_log_url)
        logparser.init_url(url=view_log_url)
        result_state = logparser.parser(client)
        # print(result_state)
        if result_state.get("status") != 400 and result_state:
            # print(result_state.get('start_time'))
            logger.info(result_state)
            logger.info(list(result_state.keys()))
            return JsonResponse({"result_log": [result_state], "args_map": list(result_state.keys()), "status": 200})
        else:
            logger.info('当前任务没有获取到结果，检查任务的日志是否存在或状态是否还未结束')
            return JsonResponse(
                {"msg": "当前任务没有获取到结果，检查任务的日志是否存在或状态是否还未结束！", "status": 400,
                 "args_map": []})


@login_required(login_url='/accounts/login/')  # 设置没有登录跳转到登录页
def states_10(request, client_id):
    """
    每秒解析一次主机日志
    :param request:
    :param client_id:
    :return:
    """
    pass


def task_status(client_id, project: str, jobid: str):
    """
    获取任务运行状态
    :param client_id: 主机id
    :param project:  项目名
    :param jobid:  任务ID
    :return: 状态 finished;running;pending
    """
    try:
        client = Client.objects.filter(id=client_id).first()
        scrapyd = get_scrapyd(client)
    except Exception as e:
        logger.error(e)
        pass
    else:
        state = scrapyd.job_status(project=project, job_id=jobid)
        logger.info(project)
        logger.info(jobid)
        logger.info(state)
        return state


@login_required(login_url='/accounts/login/')  # 设置没有登录跳转到登录页
def get_finished_task(request):
    """
    获取所有应经完成的任务信息
    :param request:
    :return:
    """
    spider_taskids = []
    results = TaskStatusList().get_finished_taskid()
    if results:
        for inf in results:
            # print(inf)
            item = {
                "client_id": inf[0],
                "project": inf[-2],
                "jobid": inf[1],
                "status":inf[-1]
            }
            spider_taskids.append(item)
    return JsonResponse({"result": spider_taskids, "task_count": len(spider_taskids), "status": 200})


@login_required(login_url='/accounts/login/')  # 设置没有登录跳转到登录页
def client_info(request):
    """
    获取启用了主机节点的信息
    :param request:
    :return:
    """
    result = Client().get_enable_client()
    if result:
        print(result)
        return JsonResponse({"status": 200, "result": [v[1] for v in result]})
    return JsonResponse({"status": 200, "result": []})


# 根据主机id定时监控爬虫的状态
@login_required(login_url='/accounts/login/')  # 设置没有登录跳转到登录页
def gettaskinfo(request, client: str):
    """
    根据主机的节点id巡检节点的任务状态
    :param request:
    :param client:
    :return:
    """
    result = TaskStatusList().get_task_info(client=client)
    if result:
        spider_tasks = []
        for inf in result:
            print(inf)
            item = {
                "client_id": inf[0],
                "project": inf[-1],
                "jobid": inf[1]
            }
            status = task_status(client_id=item.get("client_id"), project=item.get("project"), jobid=item.get("jobid"))
            task = TaskStatusList.objects.filter(jobid=item.get("jobid")).values('end_time', "status").first()
            # print(not task.get("end_time"))
            try:
                if status == "finished" and not task.get("end_time"):
                    # 任务完成及没有添加完成任务的时间就修改status为finished并更新最后的完成时间
                    try:
                        # 状态设置完成并写入列表
                        # TaskStatusList.objects.filter(jobid=item.get("jobid")).update(
                        #     end_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'), status="已完成")
                        spider_tasks.append(item)
                    except Exception as e:
                        # print(e)
                        logger.error(str(e))
                elif task.get("status"):
                    # 如果状态已经是完成的则加入列表
                    spider_tasks.append(item)
            except AttributeError:
                """删除的时候，任务在加载，会存在获取到的数据已经被删除的情况"""
                return JsonResponse({"result": [], "status": 500})
        return JsonResponse({"result": spider_tasks, "status": 200})
    return JsonResponse({"result": [], "message": "该节点没有任务运行!", "status": 200})


# 按照主机节点监控爬虫的运行状态
@login_required(login_url='/accounts/login/')  # 设置没有登录跳转到登录页
def status(request):
    """
    获取当前任务的id的运行状态
    :param request:
    :param host: scrapyd的部署地址
    :param project: 项目名称
    :param jobid: 任务ID
    :return: 运行的状态
    """
    if request.method == "POST":
        results = request.POST.get("data")
        # print(results)
        client_id = request.POST.get("client_id")
        status_list = []
        for result in eval(results):
            status = task_status(client_id=client_id, project=result.get("project"), jobid=result.get("jobid"))
            task = TaskStatusList.objects.filter(jobid=result.get("jobid")).values('end_time').first()
            # print(not task.get("end_time"))
            try:
                if status == "finished" and not task.get("end_time"):
                    # 任务完成及没有添加完成任务的时间就修改status为finished并更新最后的完成时间
                    try:

                        TaskStatusList.objects.filter(jobid=result.get("jobid")).update(
                            end_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'), status="已完成")
                    except Exception as e:
                        # print(e)
                        logger.error(str(e))
            except AttributeError:
                """删除的时候，任务在加载，会存在获取到的数据已经被删除的情况"""
                pass

            status_list.append(status)
        logger.info(status_list)
        return JsonResponse({"state": status_list, "status": 200})


@login_required(login_url='/accounts/login/')  # 设置没有登录跳转到登录页
def task_del(request):
    """
    批量删除任务
    :param request:
    :param jobid:
    :return:
    """
    if request.method == "POST":
        tasks = request.POST.get("data")
        # print(tasks)
        count = 0
        client_id = request.POST.get("client_id")
        try:
            for task in eval(tasks):
                pro_job = {
                    "project": task.split(":")[0],
                    "jobid": task.split(":")[1]
                }
                if task_status(client_id=client_id, project=pro_job.get("project"),
                               jobid=pro_job.get("jobid")) != "running":
                    TaskStatusList.objects.filter(jobid=pro_job.get("jobid")).delete()
                    count += 1
                else:
                    continue
        except Exception as e:
            logger.error(e)
            return JsonResponse({'msg': e, 'status': 400})
        return JsonResponse({'msg': '删除成功', 'status': 200, "count": count})


@login_required(login_url='/accounts/login/')  # 设置没有登录跳转到登录页
def task_cancel(request):
    """
    批量取消任务
    :param client_id: 客户端
    :param request:
    :return:
    """
    if request.method == "POST":
        task_cancels = request.POST.get("data")
        client_id = request.POST.get("client_id")
        client = Client.objects.filter(id=client_id).first()
        scrapyd = get_scrapyd(client)
        if task_cancels:
            try:
                for task in eval(task_cancels):
                    pro_job = {
                        "project": task.split(":")[0],
                        "jobid": task.split(":")[1]
                    }
                    scrapyd.cancel(project=pro_job.get("project"), job=pro_job.get("jobid"))
            except Exception as e:
                logger.error(e)
                return JsonResponse({"msg": e, "status": 400})
    logger.info("取消成功")
    return JsonResponse({"msg": "取消成功", "status": 200})


@login_required(login_url='/accounts/login/')  # 设置没有登录跳转到登录页
def task_one_cancel(request, project: str, jobid: str, client_id: str):
    """
   取消任务
   :param request:
   :param project:
   :param jobid:
   :return:
   """
    # print(project, jobid)
    try:
        client = Client.objects.filter(id=client_id).first()
        scrapyd = get_scrapyd(client)
        scrapyd.cancel(project=project, job=jobid)
    except Exception as e:
        logger.error(e)
        return JsonResponse({"msg": e, "status": 400})
    logger.info("取消成功")
    return JsonResponse({"msg": "取消成功", "status": 200})


@login_required(login_url='/accounts/login/')  # 设置没有登录跳转到登录页
def run(request):
    """
    获取爬虫规则并运行爬虫
    :param request:
    :return:
    """
    # TODO：将scrapyd的域名及端口动态化，方便多机运行部署
    if request.method == "POST":
        data = request.POST.get('data', '')
        if data:
            data = data.replace("true", "True").replace('false', 'False')  # json数据的bool值替换
            try:
                # 获取第一个主机默认为通用爬虫部署主机，存在就获取第一个，不存在就获取配置信息的主机信息
                client = Client.objects.get(id=1)
            except Exception as e:
                logger.error(e)
                logger.error("客户机不存在使用默认的住居127.0.0.1:6800")
                scrapyd = scrapydconf.scrapyd_init()
            else:
                scrapyd = get_scrapyd(client)
            try:
                job_ids = []
                runspider = {}
                data = eval(json.loads(data))
                # print(data)
                project = scrapydconf.project

                jobid = scrapyd.schedule(project=project, spider=data.get("spider"),
                                         **{"data": json.dumps(data)})
                # print(jobid)
                job_ids.append(jobid)
                runspider.update({"jobid": job_ids, "status": 200})
                TaskStatusList.objects.create(project=project, spidername=data.get("spider"),
                                              rulefile=data.get("name"), status="",
                                              jobid=jobid, client=client)
                # print(result)
                logger.info(f"{data.get('name')}:爬虫运行成功-{runspider.get('jobid')}")
                return JsonResponse(runspider, safe=False, json_dumps_params={'ensure_ascii': False})
            except Exception as e:
                # print(e)
                logger.error(e)
                return JsonResponse({"msg": f"报错了{e}", "status": 0}, safe=False,
                                    json_dumps_params={'ensure_ascii': False})
        else:
            runspider = {"status": 0, "msg": "数据为空"}
            logger.info("数据为空")
            return JsonResponse(runspider, safe=False, json_dumps_params={'ensure_ascii': False})
    else:
        logger.warning("不支持GET请求")
        return HttpResponse("不支持GET请求")


def get_filepaths(directory):
    """
    将生成目录中的文件名
    通过自顶向下或自底向上遍历树。 为每一个
    根目录top的树中的目录(包括top本身)，
    它会产生一个3元组(dirpath, dirnames, filename)
    """
    file_paths = []  # 该列表将存储所有完整的文件路径

    for root, directories, files in os.walk(directory):
        for filename in files:
            # 连接两个字符串以形成完整的文件路径。
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)
    logger.info(f"获取所有的文件路径-{file_paths}")
    return file_paths


@login_required(login_url='/accounts/login/')  # 设置没有登录跳转到登录页
def index(request):
    # 获取当前文件下的所有的文件
    file = get_filepaths("spider/configs")
    # print(file)
    logger.info(file)
    return render(request, 'spider/spider.html', {"files": [f.split("/")[-1] for f in file]})


@login_required(login_url='/accounts/login/')  # 设置没有登录跳转到登录页
def getcode(request):
    """"
    预览及编辑爬虫规则
    """
    filename = request.GET.get("filename")
    # print(filename)
    if filename:
        flag = os.path.exists(os.path.join(EDIT_FOLDER, filename))
        # print(flag)
        if flag:
            shutil.copyfile(os.path.join(EDIT_FOLDER, filename),
                            os.path.join(EDIT_FOLDER,
                                         filename.split(".")[0] + "1" + "." + filename.split(".")[1]))  # COPY副本处理文件
            with open(os.path.join(EDIT_FOLDER, filename), "r+") as f:
                code = f.readlines()
            # print(code)
            os.remove(os.path.join(EDIT_FOLDER, filename.split(".")[0] + "1" + "." + filename.split(".")[1]))
            logger.info(f"获取代码-{filename}成功!")
            return JsonResponse({"code": "".join(code), "status": 200})
        else:
            logger.warning("获取代码文件路径不存在!")
            return JsonResponse({"status": 1})
    else:
        logger.warning("未获取到文件名!")
        return JsonResponse({"status": 1})


@login_required(login_url='/accounts/login/')  # 设置没有登录跳转到登录页
def updatecode(request):
    """
    保存更新的爬虫规则
    :param request:
    :return:
    """
    if request.method == "POST":
        code = request.POST.get("data")
        filename = request.POST.get("filename")
        if "json" in filename or "py" in filename:
            flag = os.path.exists(os.path.join(EDIT_FOLDER, filename))
            if flag:
                try:
                    with open(os.path.join(EDIT_FOLDER, filename), "w+", encoding='utf-8') as f:
                        f.write(code)
                except Exception as e:
                    # print(e)
                    logger.error(e)
                    return JsonResponse({"status": 0, "msg": e})
                else:
                    logger.info(f"更新代码成功-{filename}")
                    return JsonResponse({"status": 200})
            else:
                try:
                    with open(os.path.join(EDIT_FOLDER, filename), "w+", encoding='utf-8') as f:
                        f.write(code)
                except Exception as e:
                    logger.error(e)
                    return JsonResponse({"status": 0, "msg": e})
                else:
                    return JsonResponse({"status": 200})


@login_required(login_url='/accounts/login/')  # 设置没有登录跳转到登录页
def createfile(request):
    """
    创建新的爬虫规则文件
    :param request:
    :return:
    """
    newfile = request.POST.get("newfile")
    ftype = request.POST.get("ftype")
    if newfile:
        flag = os.path.exists(os.path.join(EDIT_FOLDER, newfile + '.' + ftype))
        if not flag:
            with open(os.path.join(EDIT_FOLDER, newfile + '.' + ftype), "a+", encoding='utf-8') as f:
                f.write("")
            logger.info(f"创建文件成功-{newfile}.{ftype}!")
            return JsonResponse({"status": 200})
        else:
            logger.warning("文件名已经存在")
            return JsonResponse({"status": 0, "msg": "文件名已经存在"})


@login_required(login_url='/accounts/login/')  # 设置没有登录跳转到登录页
def removefile(request, rulefile):
    """
    删除爬虫规则
    :param rulefile: 规则名称
    :param request:
    :return:
    """
    try:
        flag = os.path.exists(os.path.join(EDIT_FOLDER, rulefile))  # 判断文件是否存在
        if flag:
            os.remove(os.path.join(EDIT_FOLDER, rulefile))  # 存在就移除
            logger.info(f"删除文件成功-{rulefile}")
        else:
            logger.warning("规则不存在!")
            return JsonResponse({"status": 400, "msg": "规则不存在!"})
    except Exception as e:
        logger.error(e)
        return JsonResponse({"status": 400, "msg": str(e)})
    else:
        return JsonResponse({"status": 200})


@login_required(login_url='/accounts/login/')  # 设置没有登录跳转到登录页
def visual_editor(request):
    """
    爬虫可视化配置
    :param request:
    :return:
    """
    return render(request, 'spider/spider_visual_editor.html')


@login_required(login_url='/accounts/login/')  # 设置没有登录跳转到登录页
def create_save_file(request):
    """
    创建并保存配置的爬虫规则到json文件
    :param request:
    :return:
    """
    if request.method == "POST":
        data = request.POST.get("data", "")
        data.replace("true", "True").replace('false', 'False')  # json数据的bool值替换
        if data:
            data1 = json.loads(data)
            newfile = data1.get("name")
            flag = os.path.exists(os.path.join(EDIT_FOLDER, newfile + ".json"))
            if not flag:
                with open(os.path.join(EDIT_FOLDER, newfile + '.json'), "a+", encoding='utf-8') as f:
                    f.write(data)
                logger.info(f"创建文件成功-{newfile}.json!")
                return JsonResponse({"status": 200, "msg": "创建及保存成功!"})
            else:
                try:
                    with open(os.path.join(EDIT_FOLDER, newfile + ".json"), "w+", encoding='utf-8') as f:
                        f.write(data)
                except Exception as e:
                    # print(e)
                    logger.error(e)
                    return JsonResponse({"status": 400, "msg": e})
                else:
                    logger.info(f"更新代码成功-{newfile}")
                    return JsonResponse({"status": 200, "msg": "保存及更新成功!"})


def task_unabled(request, jobid: str, mode: int):
    """
    任务设置取消邮件通知功能
    :param request:
    :param jobid: 任务🆔id
    :param mode: 1.启用 2.关闭
    :return: json
    """
    if request.method == "GET":
        try:
            if jobid and mode == 1:
                result = TaskStatusList().set_notifications_enable(jobid=jobid)
                if result:
                    return JsonResponse({"status":200})
                else:
                    return JsonResponse({"status":500})
            elif jobid and mode == 2:
                result = TaskStatusList().set_notifications_disable(jobid=jobid)
                if result:
                    return JsonResponse({"status": 200})
                else:
                    return JsonResponse({"status": 500})
            else:
                return JsonResponse({"status": 500})
        except Exception as e:
            return JsonResponse({"status": 500,"message":str(e)})
    else:
        pass


def notification_enable(request, jobid: str, mode: int):
    """
    任务设置邮件通知功能
    :param request:
    :param jobid: 任务🆔id
    :param mode: 1.启用 2.关闭
    :return: json
    """
    if request.method == "GET":
        try:
            if jobid and mode == 1:
                result = TaskStatusList().set_notifications_enable(jobid=jobid)
                if result:
                    return HttpResponse("设置成功！该任务完成将发送邮件提醒通知！")
                else:
                    return HttpResponse("设置失败，任务不存在！")
            elif jobid and mode == 2:
                result = TaskStatusList().set_notifications_disable(jobid=jobid)
                if result:
                    return HttpResponse("设置成功,该任务不再发送邮件提醒通知！")
                else:
                    return HttpResponse("设置失败，任务不存在！")
            else:
                return HttpResponse("设置失败，不存在的任务通知类型！")
        except Exception as e:
            return HttpResponse(f"设置失败，{e}！")
    else:
        pass


@login_required(login_url='/accounts/login/')  # 设置没有登录跳转到登录页
def rm_spider_egg(request, project_name: str, cpath:str,egg_name: str):
    """
    删除部署的打包文件
    :param request:
    :param project_name:
    :param egg_name:
    :return:
    """
    print(project_name,cpath,egg_name)
    try:
        if request.method == "GET":
            result = del_file_paths(project_name,cpath,egg_name)
            if result.get("status") == 200:
                return JsonResponse(result)
            else:
                return JsonResponse(result)
    except Exception as e:
        print(e)


@login_required(login_url='/accounts/login/')  # 设置没有登录跳转到登录页
def package(request):
    """
    创建项目仓库
    :param request:
    :return:
    """
    if request.method == "GET":
        packs = []
        for pack in PackagePath.objects.all():
            packs.append({"name": pack.name, "path": pack.path,"description":pack.description,"fullpath":pack.fullpath,"created_at":pack.created_at})
        return render(request, "spider/package.html",{"packs":packs})
    if request.method == 'POST':
        flag=True
        fullpath=""
        try:
            cpath = request.POST.get("path")
            data = {
                "name": request.POST.get("name"),
                "path": request.POST.get("path"),
                "description": request.POST.get("description"),
            }
            # print(data)
            if cpath:
                path = os.path.abspath(join(os.getcwd(), PROJECTS_FOLDER))
                flag,fullpath= PackPath(basepath=path,path=cpath).create_folder()
                # print(flag,fullpath)
            if flag:
                data.update({"fullpath": fullpath})
                if PackagePath.objects.filter(path=cpath).first():
                    PackagePath.objects.filter(path=cpath).update(**data)
                    return JsonResponse({"status": 300}, safe=False)
                PackagePath.objects.create(**data)
            else:
                return JsonResponse({"status": 400, "msg": "创建失败"}, safe=False)
        except Exception as e:
            # print(e)
            logger.error(e)
            logger_spider.error(e)
            return JsonResponse({"status": 400, "msg": str(e)}, safe=False)
        logger.info(f"{path}:项目仓库创建成功!-{data}")
        return JsonResponse({"status": 200}, safe=False)


@login_required(login_url='/accounts/login/')  # 设置没有登录跳转到登录页
def package_project(request):
    """
    渲染所属仓库的项目
    :param request:
    :param pk_name:仓库名
    :return: json
    """
    global projects
    projects=[]
    if request.method == "GET":
        pk_name = request.GET.get("name")
        try:
            model = PackagePath.objects.filter(path=pk_name)
            for pro in model:
                names=PackPath(basepath="",path=pro.fullpath).get_folder_name()
                for name in names:
                    projects.append(
                        {"name": name, "package": pk_name, "cname": pro.name, "client": ""})

                logger.info(f"获取待仓库项目:{pro}")
        except Exception as e:
            logger.error(e)
            logger_spider.error(e)
            return JsonResponse({"msg": str(e), "status": 400}, safe=False)
    elif request.method == "POST":
        pk_name = request.GET.get("name")
        try:
            model = PackagePath.objects.filter(path=pk_name)
            for pro in model:
                names = PackPath(basepath="", path=pro.fullpath).get_folder_name()
                for name in names:
                    projects.append({"name": name, "package": pk_name, "cname": pro.name,"client":""})

        except Exception as e:
            logger.error(e)
            logger_spider.error(e)
            return JsonResponse({"msg": str(e), "status": 400}, safe=False)
    logger.info(f"当前项目:{projects}")
    return render(request, 'spider/projects.html', {"data": projects, "status": 200,"count":len(projects)})