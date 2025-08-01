from django.contrib import admin
from monitor.models import Notification, EmailInfo


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'project', 'spidername', 'rulefile', 'jobid', 'status', 'client', 'email_status', 'msg',
                    'start_time', 'end_time', "create_time"]
    list_filter = ("client", 'project', 'email_status')
    search_fields = ["jobid", 'spidername']


@admin.register(EmailInfo)
class EmailInfoAdmin(admin.ModelAdmin):
    pass
