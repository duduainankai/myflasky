from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms.validators import Required, Length, Email, EqualTo, Regexp
from ..models import User
from wtforms import ValidationError


class LoginForm(Form):
	email = StringField('Email', validators=
		[Required(), Length(1, 64), Email()])
	password = PasswordField('Password', validators=[Required()])
	remember_me = BooleanField('Keep me logged in')
	submit = SubmitField('Log In')


class RegisterForm(Form):
	email = StringField('Email', validators=
		[Required(), Length(1, 64), Email()])
	username = StringField('Username', validators=
		[Required(), Length(1, 64), Regexp('^[a-zA-Z][a-zA-Z0-9_.]*$', 0, 
											'Usernames must have only letters,'
											'numbers, dots or unserscores')])
	password = PasswordField('Password', validators=
		[Required(), EqualTo('password2', message='Passwords must match.')])
	password2 = PasswordField('Confirm password', validators=[Required()])
	submit = SubmitField('Register')

	def validate_email(self, field):
		if User.query.filter_by(email=field.data).first():
			raise ValidationError('Email already register')

	def validate_username(self, field):
		if User.query.filter_by(username=field.data).first():
			raise ValidationError('Username already in use.')


class ChangepasswordForm(Form):
	old_password = PasswordField('Old password', validators=[Required()])
	new_password = PasswordField('New password', validators=[Required(), 
		EqualTo('new_password2', message='Passwords must match.')])
	new_password2 = PasswordField('Confirm new password', validators=[Required()])
	submit = SubmitField('Update Password')


class PasswordResetRequestForm(Form):
	email = StringField('Email', validators=[Required(), Length(1, 64), Email()])
	submit = SubmitField('Reset Password')


class PasswordResetForm(Form):
	email = StringField('Email', validators=[Required(), Length(1, 64), Email()])
	password = PasswordField('Password', validators=
		[Required(), Length(1, 64), EqualTo('password2', 'Passwords must match')])
	password2 = PasswordField('Confirm Password', validators=[Required()])
	submit = SubmitField('Reset Password')

	def validate_email(self, field):
		if not User.query.filter_by(email=field.data).first():
			raise ValidationError('Unknown email address.')