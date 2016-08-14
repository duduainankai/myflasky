from . import api
from flask import jsonify, g, request, current_app, url_for
from ..models import User


@api.route('/users/<int:id>')
def get_user(id):
	user = User.query.get_or_404(id)
	return jsonify(user.to_json())


@api.route('/users/<int:id>/posts/')
def get_user_posts(id):
	user = User.query.get_or_404(id)
	page = request.args.get('page', 1, type=int)
	posts = user.posts.order_by(Post.timestamp.desc()).paginate(page=page, 
		per_page=current_app.config.get('FLASKY_POSTS_PER_PAGE', 10),error_out=False)
	prev = None
	next = None
	if posts.has_prev:
		prev = url_for('api.get_user_posts', page=page-1, _external=True)
	if posts.has_next:
		next = url_for('api.get_user_posts', page=page+1, _external=True)
	return jsonify({
		'posts': [post.to_json() for post in posts],
		'prev': prev,
		'next': next,
		'count': posts.total
	})


@api.route('/users/<int:id>/timeline')
def get_user_timeline(id):
	user = User.query.get_or_404(id)
	page = request.args.get('page', 1, type=int)
	posts = user.followed_posts.order_by(Post.timestamp.desc()).paginate(page=page,
		per_page=current_app.config.get('FLASKY_POSTS_PER_PAGE', 10), error_out=False)
	prev = None
	next = None
	if posts.has_prev:
		prev = url_for('api.get_user_timeline', page=page-1, _external=True)
	if posts.has_next:
		next = url_for('api.get_user_timeline', page=page+1, _external=True)
	return jsonify({
		'posts': [post.to_json() for post in posts],
		'prev': prev,
		'next': next,
		'count': posts.total
	})