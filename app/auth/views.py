# !/usr/bin/env python
#  encoding: utf-8


from . import auth
from flask import render_template, url_for, redirect, flash, request, current_app
from .forms import LoginForm, RegisterForm, ChangepasswordForm, \
		PasswordResetRequestForm, PasswordResetForm, EmailResetForm
from ..models import User
from flask.ext.login import login_user, logout_user, login_required, current_user
from .. import db
from ..email import send_email
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


@auth.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user is not None and user.verify_password(form.password.data):
			login_user(user, form.remember_me.data)
			# 用户访问未授权的URL时会显示登录表单， Flask－Login会把原地址保存在查询字符串的next参数
			return redirect(request.args.get('next') or url_for('main.index'))
		flash('Invalid username or password')
	return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
	logout_user()
	flash('You have been logged out.')
	return redirect(url_for('auth.login'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
	form = RegisterForm()
	if form.validate_on_submit():
		user = User(username=form.username.data, email=form.email.data, 
			password=form.password.data)
		db.session.add(user)
		db.session.commit()
		token = user.generate_confirmation_token()
		send_email(user.email, 'Confirm Your Account', 'auth/email/confirm', user=user, token=token)
		flash('A confirmation email has been sent to you by email.')
		return redirect(url_for('auth.login'))
	return render_template('auth/register.html', form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
	if current_user.confirmed:
		return redirect(url_for('main.index'))
	if current_user.confirm(token):
		flash('You have confirmed your account. Thanks!')
	else:
		flash('The confirmation link is invalid or has expired')
	return redirect(url_for('main.index'))


@auth.before_app_request
def before_request():
	'''
	before_app_request表示全局的请求钩子
	is_authenticated表示用户是否登录
	endpoint返回请求的端点
	'''
	if current_user.is_authenticated:
		current_user.ping()
		if not current_user.confirmed \
		and request.endpoint[:5] != 'auth.' \
		and request.endpoint != 'static':
			return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
	if current_user.is_anonymous or current_user.confirmed:
		return redirect(url_for('main.index'))
	else:
		return render_template('auth/unconfirmed.html')


@auth.route('/confirm')
@login_required
def resend_confirmation():
	token = current_user.generate_confirmation_token()
	send_email(current_user.email, 'Confirm Your Account', 'auth/email/confirm', 
		user=current_user, token=token)
	flash('A new confirmation email has been sent to you by email')
	return redirect(url_for('main.index'))


@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
	form = ChangepasswordForm()
	if form.validate_on_submit():
		if not current_user.verify_password(form.old_password.data):
			flash('Password is Wrong!')
		else:
			current_user.password = form.new_password.data
			db.session.add(current_user)
			flash('Update Password Succeed! Now You can Login!')
			return redirect(url_for('auth.login'))
	return render_template('auth/change_password.html', form=form)


@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
	if not current_user.is_anonymous:
		return redirect(url_for('main.index'))
	form = PasswordResetRequestForm()
	if form.validate_on_submit():
		u = User.query.filter_by(email=form.email.data).first()
		if u is not None:
			token = u.generate_reset_token()
			send_email(form.email.data, 'Reset Password', 'auth/email/reset_password',
				user=u, token=token)
			flash('An email with instructions to reset your password has been sent to you.')
			return redirect(url_for('auth.login'))
		else:
			flash('Wrong Email!')
	return render_template('auth/reset_password.html', form=form)



@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
	form = PasswordResetForm()
	if form.validate_on_submit():
		u = User.query.filter_by(email=form.email.data).first()
		if u.reset(token, form.password.data):
			flash('Reset Password Succeed! Now You can Login!')
			return redirect(url_for('auth.login'))
		flash('The confirmation link is invalid or has expired')
	return render_template('auth/reset_password.html', form=form)


@auth.route('/reset-email', methods=['GET', 'POST'])
@login_required
def email_reset_request():
	form = EmailResetForm()
	if form.validate_on_submit():
		token = current_user.generate_reset_email_token(form.email.data)
		send_email(form.email.data, 'Reset Email', 'auth/email/reset_email',
			user=current_user, token=token)
		flash('An email with instructions to reset your email has been sent to you.')
		return redirect(url_for('main.index'))
	return render_template('auth/reset_email.html', form=form)


@auth.route('/reset-email/<token>')
@login_required
def email_reset(token):
	if current_user.reset_email(token):
		flash('Your email has been updated!')
		return redirect(url_for('main.index'))
	flash('The confirmation link is invalid or has expired')
	return redirect(url_for('main.index'))

