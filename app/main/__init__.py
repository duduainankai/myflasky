# !/usr/bin/env python
#  encoding: utf-8

'''
创建蓝本
单脚本程序中程序实例存在于全局作用域中，可以直接通过app.route定义路由
现在使用工厂函数在运行时创建程序，只有调用了create_app()这个工厂方法后才能使用app.route修饰器
而蓝本中定义的路由处于休眠状态，只有蓝本注册到程序上后，路由才真正成为程序的一部分
'''

from flask import Blueprint

#param: 蓝本的名字、蓝本所在的包或模块(用__name__就好)
main = Blueprint('main', __name__)

#最后引入， 避免循环导入依赖关系，因为在views和errors中还要导入蓝本main
from . import views, errors
from ..models import Permission


#上下文处理器能让变量在所有模板中全局可访问
@main.app_context_processor
def inject_permissions():
	return dict(Permission=Permission)