from . import api
from ..models import Comment
from flask import request, current_app, url_for, jsonify


@api.route('/comments')
def get_comments():
	page = request.args.get('page', 1, type=int)
	comments = Comment.query.order_by(Comment.timestamp.desc()).paginate(
		page=page, per_page=current_app.get('FLASK_COMMETN_PER_PAGE', 10), error_out=False)
	prev = None
	next = None
	if comments.has_prev:
		prev = url_for('get_comments', page=page-1, _external=True)
	if comments.has_next:
		next = url_for('get_comments', page=page+1, _external=True)
	return jsonify({
		'comments': [comment.to_json() for comment in comments],
		'prev': prev,
		'next': next,
		'count': comments.total
	})


@api.route('/comments/<int:id>')
def get_comment(id):
	comment = Comment.get_or_404(id)
	return comment.to_json()