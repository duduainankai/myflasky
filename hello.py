#!/usr/bin/env python
# encoding: utf-8

from flask import Flask
from flask import make_response
from flask import redirect
from flask import render_template

from flask.ext.script import Manager 	#可指定启动方式
from flask.ext.bootstrap import Bootstrap 	#引入bootstrap
from flask.ext.moment import Moment 	#引入时间管理
from flask.ext.wtf import Form 	#引入Form基类，由Flask－WTF扩展定义
from wtforms import StringField, SubmitField, FileField 	#字段可直接从WTForms中导入
from wtforms.validators import Required 	#验证函数可直接从WTForms中导入

from datetime import datetime


app = Flask(__name__)
app.config['SECRET_KEY'] = '******'
manager = Manager(app)	#适用很多的扩展：将程序实例作为参数传给构造函数
bootstrap = Bootstrap(app)
moment = Moment(app)


class NameForm(Form):
	'''
	每一个类变量的值是相应字段类型的对象
	'''
	name = StringField('what is your name?', validators=[Required()])
	submit = SubmitField('Submit')
	#f = FileField()


@app.route('/')
def index():
	return "<h1>Hello World!</h1>"


@app.route('/user/<name>')
def user(name):
	'''
	<***>表示url中的参数
	'''
	return "<h1>Hello {}!</h1>".format(name)


@app.route('/bad')
def badrequest():
	'''
	第二个参数表示状态码，
	第三个参数表示由header构成的字典
	'''
	return '<h1>bad request!</h1>', 400


@app.route('/makeres')
def makeres():
	'''
	通过构造response的方式返回响应，构造的参数与直接返回的方式相同
	可以设置cookie
	'''
	response = make_response('<h1>This document carries a cookie!</h1>') 
	response.set_cookie('answer', '68')
	return response


@app.route('/redirect')
def redir():
	'''
	重定向方式，状态码为302
	'''
	return redirect("http://lizheming.top")


@app.route('/template', methods=['GET', 'POST'])
def template():
	'''
	默认下会在templates文件夹中寻找模板
	'''
	#return render_template('index.html')
	#return render_template('index.html', current_time=datetime.utcnow())
	name = None
	form = NameForm()
	#根据返回值决定是重新渲染表单还是处理表单提交的数据，
	#第一次访问是一个GET请求 函数返回false 
	if form.validate_on_submit():
		name = form.name.data
		form.name.data = ""
	return render_template('index.html', form=form, current_time=datetime.utcnow(), name=name)


@app.route('/template/<name>')
def templateuser(name):
	'''
	第一个参数为模版的文件名，随后的参数都是键值对，表示模板中变量的真实值
	模板中的变量可以复杂的数据结构，如列表字典等
	可以在变量名后用竖线分隔添加过滤器
	'''
	#return render_template('user.html', name=name)
	return render_template('buser.html', name=name)	# 继承自bootstrap得模板html


@app.route('/template/filter')
def templatefilter():
	'''
	在html页面中增加过滤器
	'''
	content = '<h2 style="color:red">This is a red safe filter!</h2>'
	return render_template('filter.html', content=content)


@app.route('/control/<user>')
def control(user=None):
	'''
	页面中的控制流
	'''
	return render_template('control.html', user=user)


@app.errorhandler(404)
def page_not_found(e):
	'''
	有参数e！
	'''
	return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
	return render_template('500.html'), 500


if __name__ == "__main__":
	#app.run(debug=True)
	manager.run()	#通过添加扩展的方式启动项目, python hello.py runserver --host 0.0.0.0
