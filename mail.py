# 发送邮件的测试脚本
# 修改以下的中文字符
from flask.ext.mail import Message
from hello import mail
msg = Message('test subject', sender='替换成发送邮件使用的邮箱， app.config中配置的mail_username', 
	recipients=['替换成收件人邮箱'])
msg.body = 'text body'
msg.html = '<b>HTML</b> body'
with app.app_context():
    mail.send(msg)