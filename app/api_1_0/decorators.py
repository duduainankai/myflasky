from flask import g
from functools import wraps
from .errors import forbidden


def permission_required(permission):
	def decorator(f):
		@wraps(f)
		def decoratored_function(*args, **kwargs):
			if not g.current_user.can(permission):
				return forbidden('Insufficient permissions')
			return f(*args, **kwargs)
		return decoratored_function
	return decorator