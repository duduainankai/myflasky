'''
存储配置
基类Config中包含通用配置，子类分别定义专用的配置
配置累可以定义init_app()类方法，参数是程序实例
'''


import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
	SQLALCHEMY_COMMIT_ON_TEARDOWN = True
	MAIL_SERVER = "smtp.163.com"
	MAIL_PORT = 25
	MAIL_USE_TLS = True
	MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
	MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
	FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
	FLASKY_MAIL_SENDER = os.environ.get('MAIL_USERNAME')
	FLASKY_ADMIN = os.environ.get("FLASKY_ADMIN")
	

	@staticmethod
	def init_app(app):
		pass


class DevelopmentConfig(Config):
	DEBUG = True
	#SQLALCHEMY_DATABASE_URI = os.environ.get("DEV_DATABASE_URL") or \
	#	'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')
	SQLALCHEMY_DATABASE_URI = os.environ.get("DEV_DATABASE_URL") or \
		'sqlite:///' + os.path.join(basedir, 'data.sqlite')


class TestingConfig(Config):
	TESTING = True
	SQLALCHEMY_DATABASE_URI = os.environ.get("TEST_DATABASE_URL") or \
		'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')


class ProductionConfig(Config):
	SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or \
		'sqlite:///' + os.path.join(basedir, 'data.sqlite')


config = {
	'development': DevelopmentConfig,
	'testing': TestingConfig,
	'production': ProductionConfig,

	'default': DevelopmentConfig
}