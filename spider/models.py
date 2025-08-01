from django.db import models
from django_apscheduler.models import DjangoJob


# Create your models here.
class Client(models.Model):
    """
    scrapyd服务器配置主机信息
    """
    client_choices = ((1, "启用"), (2, "关闭"))
    name = models.CharField(max_length=255, default=None)
    ip = models.CharField(max_length=255, blank=True, null=True)
    port = models.IntegerField(default=6800, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    auth = models.IntegerField(default=0, blank=True, null=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    password = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    client_enable = models.IntegerField(choices=client_choices, verbose_name="节点任务监控", default=2)

    def __str__(self):
        """
        to string
        :return: name
        """
        return self.name

    class Meta:
        # 末尾不加s
        # 中文前加u进行编码否则报编码错误
        verbose_name_plural = u'主机配置'
        indexes = [models.Index(fields=["name"])]

    def get_enable_client(self):
        """
        获取启用了节点监控的主机节点
        :return:
        """
        result = Client.objects.filter(client_enable=1).values_list(
            'id', "name")
        return result


class TaskStatusList(models.Model):
    """"
    规则爬虫运行的任务状态表
    """
    notifications_choices = ((1, "启用"), (2, "关闭"))
    id = models.AutoField(primary_key=True)
    project = models.CharField(max_length=200, verbose_name="爬虫项目")
    spidername = models.CharField(max_length=200, verbose_name="爬虫名称")
    rulefile = models.CharField(max_length=200, verbose_name="规则名称")
    jobid = models.CharField(max_length=300, verbose_name="运行任务ID")
    status = models.CharField(max_length=300, verbose_name="运行状态", blank=True, null=True)
    start_time = models.DateTimeField(auto_now_add=True, verbose_name="开始时间")
    end_time = models.DateTimeField(blank=True, null=True, verbose_name="完成时间")
    client = models.ForeignKey(Client, unique=False, on_delete=models.DO_NOTHING)
    notifications_enable = models.IntegerField(choices=notifications_choices, verbose_name="邮件通知启用", default=1)
    package = models.CharField(max_length=255, null=True, blank=True,verbose_name="项目仓库")

    def __str__(self):
        return self.spidername

    class Meta:
        # 末尾不加s
        # 中文前加u进行编码否则报编码错误
        verbose_name_plural = u'运行任务'
        indexes = [models.Index(fields=["project", 'spidername', "jobid", "notifications_enable"])]
        ordering = ['-id']

    def get_finished_taskid(self):
        """
        获取所有已经完成的任务信息，启用了邮箱通知的，且状态为已完成的
        :return:
        """
        result = TaskStatusList.objects.filter(status="已完成").values_list(
            'client', 'jobid', "spidername", "project","notifications_enable")
        return result

    def get_task_info(self, client: str, notifications_enable: int = 1):
        """
        根据节点client获取任务的项目名、爬虫名、jobid
        notifications_enable: 默认启用了监控的爬虫
        :return:
        """
        result = TaskStatusList.objects.filter(client=client, notifications_enable=notifications_enable).values_list(
            'client', 'jobid', "spidername", "project")
        return result

    def set_notifications_enable(self, jobid: str):
        """
        设置notifications_enable任务通知启用
        :return:
        """
        try:
            result = TaskStatusList.objects.filter(jobid=jobid)
            result.update(notifications_enable=1)
        except Exception as e:
            pass
        else:
            return result

    def set_notifications_disable(self, jobid: str):
        """
        设置notifications_enable任务通知不否启用
        :return:
        """
        try:
            result = TaskStatusList.objects.filter(jobid=jobid)
            result.update(notifications_enable=2)
            print(result)
        except Exception as e:
            pass
        else:
            return result


class TaskCron(models.Model):
    """
    定时任务运行的规则配置
    """
    id = models.AutoField(primary_key=True)
    project = models.CharField(max_length=200, verbose_name="爬虫项目")
    spidername = models.CharField(max_length=200, verbose_name="爬虫名称")
    rulefile = models.CharField(max_length=200, verbose_name="规则名称")
    configuration = models.TextField(max_length=500, blank=True, null=True, verbose_name="定时任务的详情")
    job = models.ForeignKey(DjangoJob, unique=False, on_delete=models.CASCADE)  # 定时任务的关联id
    def __str__(self):
        return self.rulefile

    class Meta:
        # 末尾不加s
        # 中文前加u进行编码否则报编码错误
        verbose_name_plural = u'定时任务'
        indexes = [models.Index(fields=["rulefile"])]
        ordering = ['-id']




class PackagePath(models.Model):
    """
    项目存储路径
    """
    path = models.CharField(max_length=255,blank=True,null=True)
    name = models.TextField(max_length=255, blank=True, null=True)
    description = models.TextField(max_length=255, blank=True, default='')
    fullpath = models.TextField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        """
        to string
        :return: name
        """
        return self.description
    class Meta:
        # 末尾不加s
        # 中文前加u进行编码否则报编码错误
        verbose_name_plural = u'项目仓库'


class Project(models.Model):
    """
    爬虫项目
    """
    name = models.CharField(max_length=255, default=None)
    description = models.CharField(max_length=255, null=True, blank=True)
    egg = models.CharField(max_length=255, null=True, blank=True)
    version = models.FloatField(max_length=100, null=True, blank=True)
    configuration = models.TextField(blank=True, null=True)
    configurable = models.IntegerField(default=0, blank=True)
    built_at = models.DateTimeField(default=None, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    clients = models.ManyToManyField(Client, through='Deploy', unique=False)
    package = models.CharField(max_length=255, null=True, blank=True)


    def __str__(self):
        """
        to string
        :return: name
        """
        return self.name

    class Meta:
        # 末尾不加s
        # 中文前加u进行编码否则报编码错误
        verbose_name_plural = u'项目打包'


class Deploy(models.Model):
    """
    部署信息
    """
    client = models.ForeignKey(Client, unique=False, on_delete=models.DO_NOTHING)
    project = models.ForeignKey(Project, unique=False, on_delete=models.DO_NOTHING)
    description = models.CharField(max_length=255, blank=True, null=True)
    deployed_at = models.DateTimeField(default=None, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        unique_together = ('client', 'project')
        # 末尾不加s
        # 中文前加u进行编码否则报编码错误
        verbose_name_plural = u'部署信息'



