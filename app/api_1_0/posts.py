from . import api
from flask import jsonify
from ..models import Post


@api.route('/posts')
def get_posts():
	posts = Post.query.all()
	return jsonify({'posts': [post.to_json() for post in posts]})


@api.route('/posts/<int:id>')
def get_post(id):
	post = Post.query.get_or_404(id)
	return jsonify({'post': post.to_json()})