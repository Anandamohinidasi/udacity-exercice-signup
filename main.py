import os
import jinja2
import webapp2
import string
import re
import hmac

from google.appengine.ext import db
from google.appengine.ext.db import metadata

# setting up jinja template and path
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

# setting up standart Handler class from wich all path classes'll herdar, along with jinga
# setting for template's handler
class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw): 
	self.response.out.write(*a, **kw)
    def render_str(self, template, **params):
	t = jinja_env.get_template(template)
	return t.render(params)
    def render(self, template, **kw):
	self.write(self.render_str(template, **kw))

# class for users indentitie at datastore
class Users(db.Model):
	name = db.StringProperty(required = True)
	password = db.StringProperty(required = True)
	email = db.EmailProperty(required = False)

class MainPage(Handler): 	   	
    def get(self):
	self.render('auth.html' , data = {})
    def post(self):
	mismatch = False
	username, param = self.request.get('username'), self.request.get('username')
	password = self.request.get('password')
	verify = self.request.get('verify')
	email = self.request.get('email')
	exists = False
	# stored_usernames = db.GqlQuery("SELECT * FROM Users WHERE name = %s)" % str(username))
	# stored_usernames = metadata.get_properties_of_kind('Users', start=None, end=None) 
	v = Users.all().filter('name =', username)
	print 'haribol'
	if v.get():
		print 'tem'
		exists = True
	
        else:
		if (email):	
			# compile to check regular expression pattern
			p = re.compile('^[\S]+@[\S]+.[\S]+$')
			email = p.match(email) # check if email matchs the pattern, if no retur None to email var
			if email:
				email = True
			else:
				email = 'invalid'
		if 21>len(password)>2:
			if password!=verify:
				mismatch = True
		else:
			password = False
		if (' ' in username):
			username = True
		else:
			if 21>len(username)>2:
				username = False
			else:
				username = True
	
	if (exists == True or mismatch == True or username == True or password == False or email=='invalid'):
		self.render('auth.html', data = {'username': self.request.get('username'), 
						'email': self.request.get('email'), 'mismatch': mismatch, 
						'usernameInvalid': username,
						'password': password, 'emailValid': email, 'exists': exists})
	else:	
		username = str(self.request.get("username"))
		password =  str(self.request.get("username"))
		password = '%s|%s' % (password, hmac.new('haribol', password).hexdigest())
		usuario = Users(name = username, password = password)
		usuario.put()
		user_id = usuario.key().id()
		self.response.headers.add_header('Set-Cookie', 'userid=%s, path=/' % user_id)
		self.redirect('/welcome')

class Welcome(Handler):
	def get(self):	
	    """
	    cookie = self.request.cookies.get("user")
	    def hash_str(cookie):
		cookie =cookie.split('|',1)
		return [cookie[0], '%s|%s' % (cookie[0] , hmac.new('haribol',cookie[0]).hexdigest())]
	    if cookie == hash_str(cookie)[1]:
		radhe = hash_str(cookie)[0]
	    else: 
		radhe = 'no such a user'
		
	    self.render('welcome.html', username = radhe)
	    """
	    cookie = self.request.cookies.get("userid")
	    users = db.GqlQuery("SELECT * FROM Users where __key__ = KEY('Users', %s)" % long(cookie))
	    self.render('welcome.html', username = users)
		 
app = webapp2.WSGIApplication([
    ('/signup', MainPage), ('/welcome', Welcome)
], debug=True)
