# !/usr/bin/env python
#  encoding: utf-8
'''
复习装饰器的内容
'''


from functools import wraps
import types


def log(func):
	@wraps(func)
	def wrapper(*args, **kwargs):
		print 'begin'
		func(*args, **kwargs)
		print 'end'
	return wrapper


def log2(text='default'):
	def decorator(func):
		@wraps(func)
		def wrapper(*args, **kwargs):
			print '{} begin'.format(text)
			func(*args, **kwargs)
			print 'end'
		return wrapper
	return decorator


def Log(func):
	if type(func) != types.FunctionType:
		def decorator(func):
			@wraps(func)
			def wrapper(*args, **kwargs):
				func(*args, **kwargs)
			return wrapper
		return decorator
	else:
		@wraps(func)
		def wrapper(*args, **kwargs):
			func(*args, **kwargs)
		return wrapper


@log
def now():
	print 'now'


@log2()
def now2():
	print 'now2'


@Log('args')
def Now():
	print "Now"


@Log
def Now2():
	print "Now2"


if __name__ == '__main__':
	Now()
	Now2()