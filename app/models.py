# !/usr/bin/env python
#  encoding: utf-8

from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin, AnonymousUserMixin	# 包含了四个方法的默认实现
from . import login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, request, url_for
import hashlib
from markdown import markdown
import bleach
from exceptions import ValidationError

from datetime import datetime


class Follow(db.Model):
	__tablename__ = 'follows'
	follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), 
							primary_key=True)
	followed_id = db.Column(db.Integer, db.ForeignKey('users.id'), 
							primary_key=True)
	timestamp = db.Column(db.DateTime, default=datetime.utcnow)


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
	posts = db.relationship('Post', backref="author", lazy='dynamic')
	# 表示被该用户关注的用户们	该用户的id对应follows表中的follower_id字段  形成外键依赖  
	followed = db.relationship('Follow', 
		foreign_keys=[Follow.follower_id],
		backref=db.backref('follower', lazy='joined'),
		lazy='dynamic',
		cascade='all, delete-orphan')
	# 表示关注该用户的用户们	该用户的id对应follows表中的followed_id字段  形成外键依赖  
	followers = db.relationship('Follow',
		foreign_keys=[Follow.followed_id],
		backref=db.backref('followed', lazy='joined'),
		lazy='dynamic',
		cascade='all, delete-orphan')
	comments = db.relationship('Comment', backref='author', lazy='dynamic')

	def __init__(self, **kwargs):
		super(User, self).__init__(**kwargs)
		if self.role is None:
			if self.email == current_app.config.get('FLASKY_ADMIN'):
				self.role = Role.query.filter_by(permissions=0xff).first()
			if self.role is None:
				self.role = Role.query.filter_by(default=True).first()
			if self.email is not None and self.avatar_hash is None:
				self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
		self.follow(self)

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
			self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
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

	def is_following(self, user):
		return self.followed.filter_by(followed_id=user.id).first() is not None

	def is_followed_by(self, user):
		return self.followers.filter_by(follower_id=user.id).first() is not None

	def follow(self, user):
		if not self.is_following(user):
			f = Follow(follower=self, followed=user)
			db.session.add(f)
			db.session.commit()

	def unfollow(self, user):
		f = self.followed.filter_by(followed_id=user.id).first()
		if f:
			db.session.delete(f)

	@property
	def followed_posts(self):
		return Post.query.join(Follow, Follow.followed_id == Post.author_id)\
			.filter(Follow.follower_id == self.id)

	@staticmethod
	def generate_fake(count=100):
		from sqlalchemy.exc import IntegrityError
		from random import seed
		import forgery_py

		seed()
		for i in range(count):
			u  = User(email=forgery_py.internet.email_address(),
				username=forgery_py.internet.user_name(True),
				password=forgery_py.lorem_ipsum.word(),
				confirmed=True,
				name=forgery_py.name.full_name(),
				location=forgery_py.address.city(),
				about_me=forgery_py.lorem_ipsum.sentence(),
				member_since=forgery_py.date.date(True))
			db.session.add(u)
			try:
				db.session.commit()
			except IntegrityError:
				db.session.rollback()

	@staticmethod
	def add_self_follows():
		for user in User.query.all():
			if not user.is_following(user):
				user.follow(user)
				db.session.add(user)
				db.session.commit()

	def generate_auth_token(self, expiration):
		s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
		return s.dumps({'id': self.id})

	@staticmethod
	def verify_auth_token(token):
		s = Serializer(current_app.config['SECRET_KEY'])
		try:
			data = s.loads(token)
		except:
			return None
		return User.query.get(data['id'])

	def to_json(self):
		json_user = {
			'url': url_for('api.get_user', id=self.id, _external=True),
			'username': self.username,
			'member_since': self.member_since,
			'last_seen': self.last_seen,
			'posts': url_for('api.get_user_posts', id=self.id, _external=True),
			'followed_posts': url_for('api.get_user_followed_posts', id=self.id, _external=True),
			'post_count': self.posts.count()
		}
		return json_user


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
    COMMENT = 0X02
    WRITE_ARTICLES = 0X04
    MODERATE_COMMENTS = 0X08
    ADMINISTER = 0X80


class Post(db.Model):
	__tablename__ = 'posts'
	id = db.Column(db.Integer, primary_key=True)
	body = db.Column(db.Text)
	body_html = db.Column(db.Text)
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	comments = db.relationship('Comment', backref='post', lazy='dynamic')

	@staticmethod
	def generate_fake(count=100):
		from random import seed, randint
		import forgery_py

		seed()
		user_count = User.query.count()
		for i in range(count):
			u = User.query.offset(randint(0, user_count - 1)).first()
			p = Post(body=forgery_py.lorem_ipsum.sentences(randint(1,3)),
					timestamp=forgery_py.date.date(True),
				author=u)
			db.session.add(p)
			db.session.commit()

	@staticmethod
	def on_changed_body(target, value, oldvalue, initiator):
		allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']
		a = markdown(value, output_format='html')
		b = bleach.clean(a, tags=allowed_tags, strip=True)
		target.body_html = bleach.linkify(b)

	def to_json(self):
		json_post = {
			'url': url_for('api.get_post', id=self.id, _external=True),
			'body': self.body,
			'body_html': self.body_html,
			'timestamp': self.timestamp,
			'author': url_for('api.get_user', id=self.author_id, _external=True),
			'comments': url_for('api.get_comments', id=self.id, _external=True),
			'comment_count': self.comments.count()
		}
		return json_post

	@staticmethod
	def from_json(json_post):
		body = json_post.get('body')
		if body is None or body == '':
			raise ValidationError('post does not have a body')
		return Post(body=body)

db.event.listen(Post.body, 'set', Post.on_changed_body)


class Comment(db.Model):
	__tablename__ = 'comments'
	id = db.Column(db.Integer, primary_key=True)
	body = db.Column(db.Text)
	body_html = db.Column(db.Text)
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	disabled = db.Column(db.Boolean)
	author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

	@staticmethod
	def on_changed_body(target, value, oldvalue, initiator):
		allowed_tags = ['a', 'abbr', 'acronym', 'b', 'code', 'em', 'i', 'strong']
		target.body_html = bleach.linkify(bleach.clean(markdown(value, output_format='html'),
			tags=allowed_tags, strip=True))

db.event.listen(Comment.body, 'set', Comment.on_changed_body)
