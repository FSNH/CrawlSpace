from django.contrib import admin
from spider.models import Client, Project, Deploy, TaskStatusList, TaskCron,PackagePath


@admin.register(TaskStatusList)
class TaskStatusListAdmin(admin.ModelAdmin):
    list_display = ['id', 'project', 'spidername', 'rulefile', 'jobid', "notifications_enable", 'status', 'client','package',
                    'start_time', 'end_time']
    list_filter = ("client", 'notifications_enable')


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'ip', 'port', 'description', 'auth', 'username', 'password','client_enable', 'created_at',
                    'updated_at']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'description', 'egg', 'version','configuration', 'configurable', 'built_at','package', 'created_at',
                    'updated_at']


@admin.register(Deploy)
class DeployAdmin(admin.ModelAdmin):
    list_display = ['id', 'client', 'project', 'description', 'deployed_at', 'created_at', 'created_at']
    list_filter = ("client",)


@admin.register(TaskCron)
class TaskCronAdmin(admin.ModelAdmin):
    list_display = ['id', 'project', 'spidername', 'rulefile', 'configuration', "job"]

@admin.register(PackagePath)
class PackagePathAdmin(admin.ModelAdmin):
    list_display = ['id', 'name','path', 'description', 'fullpath','created_at', 'updated_at']

# 修改网页title和站点header。
admin.site.site_title = "爬虫探索空间站"
admin.site.site_header = "CrawlSpace"
