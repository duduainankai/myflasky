# !/usr/bin/env python
#  encoding: utf-8

from flask import render_template, abort, redirect, url_for, flash, request, current_app
from ..models import User, Role, Permission, Post, Permission
from .forms import EditProfileForm, EditProfileAdminForm, PostForm
from .. import db
from flask.ext.login import current_user, login_required
from ..decorators import admin_required, permission_required

from . import main


@main.route("/", methods=['GET', 'POST'])
def index():
	#return render_template('index.html')
	form = PostForm()
	if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
		post = Post(body=form.body.data, author=current_user._get_current_object())
		db.session.add(post)
		return redirect(url_for('.index'))
	page = request.args.get('page', 1, type=int)
	pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page, 
		per_page=current_app.config.get('FLASK_POSTS_PER_PAGE', 10), error_out=False)
	#posts = Post.query.order_by(Post.timestamp.desc()).all()
	posts = pagination.items
	return render_template('index.html', form=form, posts=posts, Permission=Permission, pagination=pagination)


@main.route("/user/<username>")
def user(username):
	user = User.query.filter_by(username=username).first()
	if not user:
		abort(404)
	posts = user.posts.order_by(Post.timestamp.desc()).all()
	return render_template("user.html", user=user, posts=posts, Permission=Permission)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
	form = EditProfileForm()
	if form.validate_on_submit():
		current_user.name = form.name.data
		current_user.location = form.location.data
		current_user.about_me = form.about_me.data
		db.session.add(current_user)
		flash('Your profile has been updated.')
		return redirect(url_for('.user', username=current_user.username))
	form.name.data = current_user.name
	form.location.data = current_user.location
	form.about_me.data = current_user.about_me
	return render_template("edit_profile.html", form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
	user = User.query.get_or_404(id)
	form = EditProfileAdminForm(user=user)
	if form.validate_on_submit():
		user.email = form.email.data
		user.username = form.username.data
		user.confirmed = form.confirmed.data
		user.role = Role.query.get(form.role.data)
		user.name = form.name.data
		user.location = form.location.data
		user.about_me = form.about_me.data
		db.session.add(user)
		flash('The profile has been updated.')
		return redirect(url_for('.user', username=user.username))
	form.email.data = user.email
	form.username.data = user.username
	form.confirmed.data = user.confirmed
	form.role.data = user.role_id
	form.name.data = user.name
	form.location.data = user.location
	form.about_me.data = user.about_me
	return render_template('edit_profile.html', form=form, user=user)


@main.route('/post/<int:id>')
def post(id):
	post = Post.query.get_or_404(id)
	return render_template('post.html', posts=[post])


@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
	post = Post.query.get_or_404(id)
	if current_user != post.author and not current_user.is_administrator:
		abort(403)
	form = PostForm()
	if form.validate_on_submit():
		post.body = form.body.data
		db.session.add(post)
		flash('The post has been updated.')
		return redirect(url_for('.post', id=post.id))
	form.body.data = post.body
	return render_template('edit_post.html', form=form)


@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
	u = User.query.filter_by(username=username).first()
	if u is None:
		flash('Invalid user.')
		return redirect(url_for('.index'))
	if current_user.is_following(u):
		flash('You are already following this user.')
		return redirect(url_for('.user', username=username))
	current_user.follow(u)
	db.session.add(current_user)
	flash('You are now following %s.' % username)
	return redirect(url_for('.user', username=username))


@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
	u = User.query.filter_by(username=username).first()
	if u is None:
		flash('Invalid user.')
		return redirect(url_for('.index'))
	if not current_user.is_following(u):
		flash('You have not following this user.')
		return redirect(url_for('.user', username=username))
	current_user.unfollow(u)
	db.session.add(current_user)
	flash('You are now unfollowing %s.' % username)
	return redirect(url_for('.user', username=username))


@main.route('/followers/<username>')
@login_required
def followers(username):
	user = User.query.filter_by(username=username).first()
	if user is None:
		flash('Invalid user.')
		return redirect(url_for('.index'))
	page = request.args.get('page', 1, type=int)
	pagination = user.followers.paginate(
		page, per_page=current_app.config.get('FLASK_FOLLOWERS_PER_PAGE',10),error_out=False)
	followers = [{'user': item.follower, 'timestamp': item.timestamp} for item in pagination.items]
	return render_template('followers.html', pagination=pagination, followers=followers, user=user)



@main.route('/followed_by/<username>')
@login_required
def followed_by(username):
	u = User.query.filter_by(username=username).first()
	if u is None:
		flash('Invalid user.')
		return redirect(url_for('.index'))	

