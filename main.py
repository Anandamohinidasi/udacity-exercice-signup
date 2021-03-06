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
		password =  str(self.request.get("password"))
		password = '%s|%s' % (password, hmac.new('haribol', password).hexdigest())
		usuario = Users(name = username, password = password)
		usuario.put()
		user_id = usuario.key().id()
		user_id = '%s|%s' % (str(user_id), hmac.new('haribol', str(user_id)).hexdigest())
		self.response.headers.add_header('Set-Cookie', 'user_ID=%s, path=/' % user_id)
		self.redirect('/welcome')

class Welcome(Handler):
	def get(self):	
	    cookie = self.request.cookies.get("user_ID")
	    if cookie:	
		    cookie_list = cookie.split('|')
		    print 'Primeira parte: %s ; Segunda parte: %s' % (cookie_list[0], cookie_list[1],)
		    if cookie_list[1] == hmac.new('haribol', cookie_list[0]).hexdigest():
			   users = 'test'	
			   users = db.GqlQuery("SELECT * FROM Users where __key__ = KEY('Users', %s)" % long(cookie_list[0]))
			   self.render('welcome.html', username = users)
		    else:
			   self.render('auth.html', data={})
            else:
		    self.redirect('/signup')

class LoginHandler(Handler):
	def get(self):
		self.render('login.html')
	def post(self):
		username = self.request.get('username')
		password = self.request.get('password')
		v = Users.all().filter('name =', username)
		a = Users.all().filter('password =', '%s|%s' % (password,hmac.new('haribol', password).hexdigest()))
		if v.get() and a.get():
			print 'analisou e aprovou, o username eh: %s e a senha eh: %s' % (username,password)
			# users = db.GqlQuery("SELECT * FROM Users where name = %s" % username) 			
			user_id = v.get().key().id()
			user_id = '%s|%s' % (str(user_id), hmac.new('haribol', str(user_id)).hexdigest())			
			self.response.headers.add_header('Set-Cookie', 'user_ID=%s, path=/' % user_id)
			self.redirect('/welcome')
		else:		
			print 'analisou e nao aprovou'
			self.render('login.html', invalid = True)	 
class LogoutHandler(Handler):
	def get(self):
		none = ''
		self.response.headers.add_header('Set-Cookie', 'user_ID=%s, path=/' % none)
		self.response.headers.add_header('Set-Cookie', 'userid=%s, path=/' % none)
		self.redirect('/signup')
		 
app = webapp2.WSGIApplication([
    ('/signup', MainPage), ('/welcome', Welcome), ('/login', LoginHandler), ('/logout', LogoutHandler)
], debug=True)
