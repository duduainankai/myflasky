# !/usr/bin/env python
#  encoding: utf-8

from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin	# 包含了四个方法的默认实现
from . import login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app


class User(UserMixin, db.Model):
	__tablename__ = "users"
	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(64), unique=True, index=True)
	username = db.Column(db.String(64), unique=True, index=True)
	password_hash = db.Column(db.String(128))
	confirmed = db.Column(db.Boolean, default=False)
	role_id = db.Column(db.Integer, db.ForeignKey("roles.id"))

	def __repr__(self):
		return '<User %r>' % self.username

	@property
	def password(self):
		raise AttributeError('password is not a readable attribute')

	@password.setter
	def password(self, password):
		self.password_hash = generate_password_hash(password)

	def verify_password(self, password):
		return check_password_hash(self.password_hash, password)

	def generate_confirmation_token(self, expiration=3600):
		s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
		return s.dumps({'confirm': self.id})

	def confirm(self, token):
		s = Serializer(current_app.config['SECRET_KEY'])
		try:
			data = s.loads(token)
		except Exception, e:
			return False
		if data.get('confirm') != self.id:
			return False
		self.confirmed = True
		db.session.add(self)
		return True

	def generate_reset_token(self, expiration=3600):
		s = Serializer(current_app.config["SECRET_KEY"])
		token = s.dumps({"reset" : self.id})
		return token

	def reset(self, token, password):
		s = Serializer(current_app.config["SECRET_KEY"])
		try:
			data = s.loads(token)
		except Exception, e:
			return False
		if data.get("reset") == self.id:
			self.password = password
			db.session.add(self)
			db.session.commit()
			return True
		return False


# flask－login要求实现的回调函数 使用指定的标识符加载用户
@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))


class Role(db.Model):
	__tablename__ = "roles"
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), unique=True)

	users = db.relationship('User', backref='role', lazy='dynamic')

	def __repr__(self):
		return '<Role %r>' % self.name