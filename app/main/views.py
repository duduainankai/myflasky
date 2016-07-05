# !/usr/bin/env python
#  encoding: utf-8

from datetime import datetime
from flask import render_template, session, redirect, url_for, current_app

from . import main
from .forms import NameForm
from .. import db
from ..models import User, Role
from ..email import send_email

from flask.ext.login import login_required	# 添加该修饰器表示保护路由，只让认证用户访问


@main.route("/", methods=['GET', 'POST'])
@login_required
def index():
	form = NameForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.name.data).first()
		if user is None:
			user = User(username=form.name.data)
			db.session.add(user)
			session['known'] = False
			print session['known']
			if current_app.config.get("FLASKY_ADMIN"):
				print current_app.config.get("FLASKY_ADMIN")
				send_email(current_app.config.get("FLASKY_ADMIN"), "New User",
					"mail/new_user", user=user)
		else:
			session['known'] = True
		session['name'] = form.name.data
		return redirect(url_for('main.index'))
	return render_template('index.html', current_time=datetime.utcnow(),
		name=session.get('name'), form=form, known=session.get('known', False))