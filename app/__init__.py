# !/usr/bin/env python
#  encoding: utf-8

'''
延迟创建程序实例，把创建过程移到可显式调用的工厂函数中
可以给脚本留出配置程序的时间，还能够创建多个程序实例
'''

from flask import Flask 
from flask.ext.bootstrap import Bootstrap 
from flask.ext.mail import Mail 
from flask.ext.moment import Moment
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.pagedown import PageDown
from config import config

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
pagedown = PageDown()

login_manager = LoginManager()
login_manager.session_protection = 'strong'	# 设置不同的安全等级防止用户会话被篡改
login_manager.login_view = 'auth.login'	# 设置登录页面的端点


def create_app(config_name):
	'''
	工厂函数， 返回创建的程序实例，定义扩展
	保存的配置可使用app.config配置对象提供的from_object()方法直接导入
	'''
	app = Flask(__name__)
	app.config.from_object(config[config_name])
	config[config_name].init_app(app)

	bootstrap.init_app(app)
	mail.init_app(app)
	moment.init_app(app)
	db.init_app(app)
	login_manager.init_app(app)
	pagedown.init_app(app)

	'''
	注册蓝本
	'''
	from .main import main as main_blueprint
	app.register_blueprint(main_blueprint)
	
	from .auth import auth as auth_blueprint
	app.register_blueprint(auth_blueprint, url_prefix='/auth')

	from .api_1_0 import api as api_1_0_blueprint
	app.register_blueprint(api_1_0_blueprint, url_prefix='/api/v1.0')

	return app