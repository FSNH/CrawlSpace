# 导入smtplib模块
import smtplib

# 从email.mime.multipart中导入MIMEMultipart类
from email.mime.multipart import MIMEMultipart
# 从email.header中导入Header类
from email.header import Header

# 从email.mime.text中导入MIMEText类
from email.mime.text import MIMEText

# 从email.mime.image中导入MIMEImage类
from email.mime.image import MIMEImage

# 1、连接邮箱服务器
# 连接邮箱服务器：连接邮箱服务器：使用smtplib模块的类SMTP_SSL，创建一个实例对象qqMail
qqMail = smtplib.SMTP_SSL("smtp.qq.com", 465)

# 2、登陆邮箱
# 设置登录邮箱的帐号为："zhangxiaofan@qq.com"，赋值给mailUser
mailUser = "1737605956@qq.com"
# 将邮箱授权码"xxxxx"，赋值给mailPass
mailPass = "khedbretrihqbbha"
# 登录邮箱：调用对象qqMail的login()方法，传入邮箱账号和授权码
qqMail.login(mailUser, mailPass)

# 3、编辑收发件人
# 设置发件人和收件人
sender = "1737605956@qq.com"
receiver = "3314577295@qq.com"
# 使用类MIMEMultipart，创建一个实例对象message
message = MIMEMultipart()
# 将主题写入 message["Subject"]
message["Subject"] = Header("合照")
# 将发件人信息写入 message["From"]
message["From"] = Header(f"xiaofan<{sender}>")
# 将收件人信息写入 message["To"]
message["To"] = Header(f"xueqi<{receiver}>")

# 4、构建正文
# 设置邮件的内容，赋值给变量textContent
textContent = "雪琪，看我们的合影帅不帅"
# 编辑邮件正文：使用类MIMEText，创建一个实例对象mailContent
mailContent = MIMEText(textContent, "plain", "utf-8")
# 、发送邮件
# 发送邮件：使用对象qqMail的sendmail方法发送邮件
qqMail.sendmail(sender, receiver, message.as_string())
# 输出"发送成功"
print("发送成功")