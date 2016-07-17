# !/usr/bin/env python
#  encoding: utf-8

from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin, AnonymousUserMixin	# 包含了四个方法的默认实现
from . import login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, request
import hashlib

from datetime import datetime


class User(UserMixin, db.Model):
	__tablename__ = "users"
	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(64), unique=True, index=True)
	username = db.Column(db.String(64), unique=True, index=True)
	password_hash = db.Column(db.String(128))
	confirmed = db.Column(db.Boolean, default=False)
	role_id = db.Column(db.Integer, db.ForeignKey("roles.id"))
	name = db.Column(db.String(64))
	location = db.Column(db.String(64))
	about_me = db.Column(db.Text())
	member_since = db.Column(db.DateTime(), default=datetime.utcnow)
	last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
	avatar_hash = db.Column(db.String(32))

	def __init__(self, **kwargs):
		super(User, self).__init__(**kwargs)
		if self.role is None:
			if self.email == current_app.config.get('FLASKY_ADMIN'):
				self.role = Role.query.filter_by(permissions=0xff).first()
			if self.role is None:
				self.role = Role.query.filter_by(default=True).first()
			if self.email is not None and self.avatar_hash is None:
				self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()

	def __repr__(self):
		return '<User %r>' % self.username

	def can(self, permissions):
		return self.role is not None and \
			(self.role.permissions & permissions) == permissions

	def is_administrator(self):
		return self.can(Permission.ADMINISTER)

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

	def generate_reset_email_token(self, email, expiration=3600):
		s = Serializer(current_app.config['SECRET_KEY'])
		token = s.dumps({'email': email, 'id': self.id})
		return token

	def reset_email(self, token):
		s = Serializer(current_app.config['SECRET_KEY'])
		try:
			data = s.loads(token)
		except Exception, e:
			return False
		if data.get('id') == self.id and data.get('email'):
			self.email = data.get('email')
			self.avatar_hash = hashlib.md5(self.email.encode('itf-8')).hexdigest()
			db.session.add(self)
			return True
		return False

	def ping(self):
		self.last_seen = datetime.utcnow()
		db.session.add(self)

	def gravatar(self, size=100, default='identicon', rating='g'):
		if request.is_secure:
			url = "https://secure.gravatar.com/avatar"
		else:
			url = 'http://www.gravatar.com/avatar'
		hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
		return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(url=url
			, hash=hash, size=size, default=default, rating=rating)


# flask－login要求实现的回调函数 使用指定的标识符加载用户
@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))


class AnonymousUser(AnonymousUserMixin):
	def can(self, permissions):
		return False

	def is_administrator(self):
		return False


login_manager.anonymous_user = AnonymousUser


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.FOLLOW | 
                    Permission.COMMMENT | 
                    Permission.WRITE_ARTICLES, True),
            "Moderator": (Permission.FOLLOW | 
                    Permission.COMMMENT | 
                    Permission.WRITE_ARTICLES |
                    Permission.MODERATE_COMMENTS, False),
            "Administrator": (0xff, False)
        }
        for r, p in roles.iteritems():
            if not Role.query.filter_by(name=r).first():
                role = Role(name=r, permissions=p[0], default=p[1])
                db.session.add(role)
        db.session.commit()


class Permission:
    FOLLOW = 0X01
    COMMMENT = 0X02
    WRITE_ARTICLES = 0X04
    MODERATE_COMMENTS = 0X08
    ADMINISTER = 0X80