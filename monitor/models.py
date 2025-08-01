from django.db import models


# Create your models here.

class Notification(models.Model):
    """
    任务邮件通知任务
    """
    id = models.AutoField(primary_key=True)
    project = models.CharField(max_length=200, verbose_name="爬虫项目")
    spidername = models.CharField(max_length=200, verbose_name="爬虫名称")
    rulefile = models.CharField(max_length=200, verbose_name="规则名称")
    client = models.CharField(max_length=300, verbose_name="主机信息")
    jobid = models.CharField(max_length=300, verbose_name="运行任务ID")
    status = models.CharField(max_length=300, verbose_name="运行状态", blank=True, null=True)
    start_time = models.CharField(max_length=50, blank=True, null=True, verbose_name="开始时间")
    end_time = models.CharField(max_length=50, blank=True, null=True, verbose_name="完成时间")
    email_status = models.CharField(max_length=50, verbose_name="邮件状态", blank=True, null=True)
    msg = models.TextField(verbose_name="邮件详情", blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    def __str__(self):
        return f"{self.jobid}-发送{self.email_status}"

    class Meta:
        # 末尾不加s
        # 中文前加u进行编码否则报编码错误
        verbose_name_plural = u'邮件通知任务'
        indexes = [models.Index(fields=["jobid"])]
        ordering = ['-create_time']


class EmailInfo(models.Model):
    TIME_CHOICES = (("H", "hour"), ("M", "minutes"), ("D", "days"))
    html_message = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Crawlspace邮件通知设置</title>
    </head>
    <body>
    <table>
            <tr>
                <th>主机</th>
                <th>项目</th>
                <th>爬虫</th>
                <th>规则</th>
                <th>任务</th>
                <th>状态</th>
                <th>开始时间</th>
                <th>结束时间</th>
            </tr>
            <tr>
            <td>{0}</td>
            <td>{1}</td>
            <td>{2}</td>
            <td>{3}</td>
            <td>{4}</td>
            <td>{5}</td>
            <td>{6}</td>
            <td>{7}</td>
        </tr>
    </table>
        <p style="font-size:30px;color:red;">爬虫造反啦！管理员快点啊！看看是不是来活了！</p>
        <p><button style="color:red"><a href="{8}">不再邮件通知该任务！</a></button></p>
    </body>
    </html>
        """
    id = models.AutoField(primary_key=True)
    email_host = models.EmailField(verbose_name="默认邮箱")
    email_port = models.CharField(max_length=50, verbose_name="邮箱端口号", default=25)
    email_host_pwd = models.CharField(max_length=100, verbose_name="授权码")
    default_from_email = models.EmailField(verbose_name="默认发件邮箱")
    subject = models.CharField(max_length=200, verbose_name="邮箱主题", default="CrawlSpace爬虫管理系统")
    from_email = models.EmailField(verbose_name="发件邮箱")
    recipient_list = models.TextField(verbose_name="收件人列表")
    email_content = models.TextField(verbose_name="邮箱模板",default=html_message)
    unit = models.CharField(max_length=10, choices=TIME_CHOICES, verbose_name="时间单位")
    interval_send_email = models.CharField(max_length=10, verbose_name="邮箱发送间隔时间")
    email_enable = models.BooleanField(default=True, verbose_name="是否启用邮箱")
    tls = models.BooleanField(default=False,verbose_name="是否启动TLS链接")
    host = models.URLField(default="http://127.0.0.1:8000", verbose_name="服务器域名")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    def __str__(self):
        return self.email_host

    class Meta:
        # 末尾不加s
        # 中文前加u进行编码否则报编码错误
        verbose_name_plural = u'邮件配置信息'
        indexes = [models.Index(fields=["email_host"])]
        ordering = ['-create_time']
