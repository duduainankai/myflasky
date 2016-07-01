#!/usr/bin/env python
# encoding: utf-8

from flask import Flask
from flask import make_response
from flask import redirect
from flask.ext.script import Manager

app = Flask(__name__)
manager = Manager(app)	#适用很多的扩展：将程序实例作为参数传给构造函数



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



if __name__ == "__main__":
	#app.run(debug=True)
	manager.run()	#通过添加扩展的方式启动项目
