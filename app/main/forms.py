# !/usr/bin/env python
#  encoding: utf-8

from flask.ext.wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required


class NameForm(Form):
	name = StringField('Whatis your name?', validators=[Required()])
	submit = SubmitField('Submit')
