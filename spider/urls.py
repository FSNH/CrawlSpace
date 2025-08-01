from django.urls import path, re_path
from . import views

app_name = "spider"
urlpatterns = [
    path('index.html', views.index, name='spiderindex'),  # 首页
    path("code/", views.getcode, name="spidercode"),  # 编辑代码
    path('updatecode/', views.updatecode, name="spiderupdate"),  # 更新代码
    path('file/', views.createfile, name="createfile"),  # 新建文件
    path(r'remove/<str:rulefile>/', views.removefile, name="removefile"),  # 移除文件
    re_path(r'run/', views.run, name="run"),  # 运行爬虫
    path(r'node/', views.node_state, name="get_node_info"),  # 获取节点信息（主机运行状态信息）
    path('list.html', views.task_list, name="tasklist"),  # 爬虫列表
    path('status/', views.status, name="status"),  # 运行状态
    path(r'del/', views.task_del, name="task_del"),  # 批量删除任务
    path(r'cancel/', views.task_cancel, name="task_cancel"),  # 批量取消任务
    path(r'cancel/<str:project>/<str:jobid>/<str:client_id>/', views.task_one_cancel, name="task_one_cancel"),  # 取消单个任务
    path(r'viewlogs/<str:project>/<str:spider>/<str:jobid>/', views.task_log, name="task_log"),  # 浏览任务日志
    path("states.html", views.node, name="nodeindex"),  # 查看节点信息
    path("states/<str:project>/<str:spidername>/<str:jobid>/", views.states, name="task_state"),  # 查看日志解析结果
    path(r'client/<int:client_id>/project/<str:project_name>/spider/<str:spider_name>/job/<str:job_id>/log/', views.job_log, name='job_log'),  # 查看实时日志
    path("server.html", views.server, name="server"),  # 查看主机信息
    path("client_create/", views.client_create, name="client"),  # 创建主机
    path("client_status/", views.client_status, name="client_status"),  # 主机状态
    path("client_del/<int:client_id>/", views.client_remove, name="client_del"),  # 删除主机
    path("deploy.html", views.deploy, name="deploy"),  # 部署首页
    path(r"build/<str:project_name>/<str:cpath>/", views.project_build, name="build"),  # 项目打包
    path(r"deploy/<str:client_id>/<str:project_name>/<str:cpath>/", views.project_deploy, name="deploy"),  # 项目部署
    path("upload.html", views.project_upload, name="upload"),  # 项目上传
    path(r"spiders/<str:client_id>/", views.spider_list, name="spider_list"),  # 获取scrapyd的爬虫
    path("project/<str:client_id>/<str:cpath>/del/", views.del_project, name='del_project'),  # 删除爬虫项目
    path("scheduler.html", views.client_project, name='projects'),  # 调度爬虫页面
    path("crawls/<str:client_id>/<str:cpath>/", views.spider_start, name='crawls'),  # 调度爬虫页面
    path("project/tree/<str:package>/<str:project_name>/", views.project_tree, name='project_tree'),  # 获取项目的树结构
    path("edit/tree/<str:package>/<str:project_name>/", views.project_code, name='project_code'),  # 项目的树结构渲染
    path("editor.html", views.visual_editor, name='visual_editor'),  # 爬虫的在线可视化配置
    path("create_save_file/", views.create_save_file, name="create_save_file"),  # 创建文件保存及更新配置
    path(r"notification/<str:jobid>/<int:mode>/", views.notification_enable, name="notification_enable"),  # 是否启用邮件通知
    path(r"task_unable/<str:jobid>/<int:mode>/", views.task_unabled, name="task_unable"),  # 一键已读消息通知通知
    path(r"rmegg/<str:project_name>/<str:cpath>/<str:egg_name>/", views.rm_spider_egg, name="del_file_paths"),  # 删除单个项目打包文件
    path("test/info/<str:client>/",views.gettaskinfo,name="getinfo"),  # 获取节点的任务状态
    path("test/info/", views.client_info, name="clientinfo"),  # 获取启用的主机节点
    path("tasks/", views.get_finished_task, name="get_finished_task"),  # 获取所有已经完成的任务
    path(r"pros/<str:pro_path>/", views.packs_projects, name="packs_pro"),  # 根据路径获取项目
    path("package.html",views.package,name="package"), # 项目仓库创建页面
    path("client_package/", views.package, name="client_package"),  # 创建项目仓库
    path("projects.html", views.package_project, name='package_project'),  # 调度爬虫页面

]
