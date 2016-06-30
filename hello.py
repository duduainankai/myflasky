from flask import Flask
from flask import request
from flask import redirect
from flask import abort
from flask.ext.script import Manager
app = Flask(__name__)
manager = Manager(app)

@app.route('/')
def index():
	user_agent = request.headers['User-Agent']
	return '<p>Your browser is {}</p>'.format(user_agent)

@app.route('/user/<name>')
def user(name):
	return '<h1>Hello {}!</h1>'.format(name)


@app.route('/user/<name>/<gender>')
def user2(name, gender):
	g = "Ms." if int(gender) == 2 else "Msr."
	return '<h1>Hello %s%s!' %(g, name)

@app.route('/badrequest')
def bad():
	return "<h1>bad request</h1>", 400

@app.route('/redirect')
def redirects():
	return redirect('http://www.baidu.com')

@app.route('/abort')
def aborts():
	abort(404)

if __name__ == "__main__":
	#app.run(debug=True)
	manager.run()