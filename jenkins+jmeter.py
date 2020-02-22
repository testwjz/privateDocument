import os
import smtplib
import sys
import zipfile
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

"""
执行脚本如：python .py  %JENKINS_URL% %JOB_NAME%
"""


# 定义基本信息
def _set_base_info(message, msg_html, receivers, *attachments):
    # 邮件基本信息
    message['From'] = Header("接口自动化测试邮件", 'utf-8')
    for i in range(len(receivers)):
        message['To'] = Header(receivers[i], 'utf-8')
    subject = 'Python SMTP 邮件测试'
    message['Subject'] = Header(subject, 'utf-8')
    # 添加正文
    body = MIMEText(msg_html, 'html', 'utf-8')
    message.attach(body)
    [_add_attachment(message, attachments[i]) for i in range(len(attachments))]


# 添加附件
def _add_attachment(message, filename):
    attachment = MIMEText(open(filename, 'rb').read(), 'plain', 'utf-8')
    attachment["Content-Type"] = 'application/octet-stream'
    attachment.add_header('Content-Disposition', 'attachment', filename=('utf-8', '', filename))
    message.attach(attachment)


# 发送邮件
def send_mail(mail_host, mail_user, mail_pass, sender,
              receivers, msg_html, *attachments):
    message = MIMEMultipart()
    _set_base_info(message, msg_html, receivers, *attachments)
    smtpObj = smtplib.SMTP()
    smtpObj.connect(mail_host, 25)  # 25 为 SMTP 端口号
    smtpObj.login(mail_user, mail_pass)
    smtpObj.sendmail(sender, receivers, message.as_string())

#遍历路径下文件
def _get_zip_file(input_path, result):
    files = os.listdir(input_path)
    for file in files:
        if os.path.isdir(input_path + '/' + file):
            _get_zip_file(input_path + '/' + file, result)
        else:
            result.append(input_path + '/' + file)


def zip_file_path(input_path, output_path, output_name):
    f = zipfile.ZipFile(output_path + '/' + output_name, 'w', zipfile.ZIP_DEFLATED)
    filelists = []
    _get_zip_file(input_path, filelists)
    for file in filelists:
        f.write(file)
    # 调用了close方法才会保证完成压缩
    f.close()

if __name__ == '__main__':
    # 获取脚本参数
    if len(sys.argv) != 6 :
        print(r"""
        参数个数不正确，脚本应该如下：
        python %WORKSPACE%\Test.py %JENKINS_URL% %JOB_NAME% %BUILD_NUMBER% %WORKSPACE% jmx文件名称
        """)
        sys.exit()

    JENKINS_URL, JOB_NAME, BUILD_NUMBER, WORKSPACE, FILE_NAME = sys.argv[1:]

    # 第三方 SMTP 服务
    mail_host = "smtp.qq.com"  # 设置服务器
    mail_user = "805340489"  # 用户名
    mail_pass = "erzkonvurlpebcgg"  # 口令
    sender = '805340489@qq.com'
    receivers = ['zhangwenjun1@dgg.net']  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱

    # 邮件正文
    msg_html = """
    <p>{1}接口测试结果</p>
    <li>测试报告地址：<a href="{0}job/{1}/HTML_20Report/">点击链接查看{1}报告</a></li>
    <li>项目构建地址：<a href="{0}job/{1}">点击链接查看{1}构建地址</a></li>
    """.format(JENKINS_URL, JOB_NAME)

    #定义报告路径
    reportDir = r"E:\Jmeter-report\{1}\Build-{0}".format(BUILD_NUMBER,FILE_NAME)
    if not os.path.exists(reportDir):
        os.mkdir(reportDir)

    #定义需要执行的shell（jmeter运行并生成报告）
    command = r"D:\apache-jmeter-5.1.1\bin\jmeter -n -t {0}\{1}.jmx -l {0}\{1}.jtl -e -o {2}".format(
        WORKSPACE,FILE_NAME,reportDir)
    os.system(command)

    #对报告进行压缩，并放在WORKSPACE中
    zip_file_path(reportDir, WORKSPACE, 'report.zip')

    #发送邮件
    send_mail(mail_host, mail_user, mail_pass, sender, receivers, msg_html, "report.zip")
    


