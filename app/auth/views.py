# !/usr/bin/env python
#  encoding: utf-8


from . import auth
from flask import render_template, url_for, redirect, flash, request
from .forms import LoginForm
from ..models import User
from flask.ext.login import login_user, logout_user, login_required


@auth.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user is not None and user.verify_password(form.password.data):
			login_user(user, form.remember_me.data)
			# 用户访问未授权的URL时会显示登录表单， Flask－Login会把原地址保存在查询字符串的next参数
			return redirect(request.args.get('next') or url_for('mail.index'))
		flash('Invalid username or password')
	return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
	logout_user()
	flash('You have been logged out.')
	return redirect(url_for('auth.login'))