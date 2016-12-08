import os
import jinja2
import webapp2
import string

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir))
class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw): 
	self.response.out.write(*a, **kw)
    def render_str(self, template, **params):
	t = jinja_env.get_template(template)
	return t.render(params)
    def render(self, template, **kw):
	self.write(self.render_str(template, **kw))
class MainPage(Handler): 	   	
    def get(self):
	self.render('auth.html' , data = {})
    def post(self):
	mismatch = False
	username = self.request.get('username')
	password = self.request.get('password')
	verify = self.request.get('verify')
	email = self.request.get('email')
	if password!=verify:
		mismatch = True
	if (' ' in username):
		username = True
	else:
		username = False
	if (mismatch == True or username == True):
		self.render('auth.html', data = {'username': self.request.get('username'), 
						'email': self.request.get('email'), 'mismatch': 						mismatch, 'usernameInvalid': username,})
	else:
		self.render('welcome.html', username = self.request.get('username'))
	 
app = webapp2.WSGIApplication([
    ('/', MainPage)
], debug=True)
