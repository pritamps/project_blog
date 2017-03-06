import os
import re
import random
import hashlib
from time import sleep
import hmac
from string import letters

import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)

secret = 'fart'


def render_str(template, **params):
    t = jinja_env.get_template(template)
    print params
    return t.render(params)


def make_secure_val(val):
    return '%s|%s' % (val, hmac.new(secret, val).hexdigest())


def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val


class BlogHandler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        params['user'] = self.user
        print params
        return render_str(template, **params)

    def render(self, template, **kw):

        self.write(self.render_str(template, **kw))

    def set_secure_cookie(self, name, val):
        cookie_val = make_secure_val(val)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (name, cookie_val))

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    def login(self, user):
        self.set_secure_cookie('user_id', str(user.key().id()))

    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))


# def render_post(response, post):
#     response.out.write('<b>' + post.subject + '</b><br>')
#     response.out.write(post.content)


class MainPage(BlogHandler):

    def get(self):
        self.write('Hello, Udacity!')


# user stuff
def make_salt(length=5):
    return ''.join(random.choice(letters) for x in xrange(length))


def make_pw_hash(name, pw, salt=None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (salt, h)


def valid_pw(name, password, h):
    salt = h.split(',')[0]
    return h == make_pw_hash(name, password, salt)


def users_key(group='default'):
    return db.Key.from_path('users', group)


class User(db.Model):
    name = db.StringProperty(required=True)
    pw_hash = db.StringProperty(required=True)
    email = db.StringProperty()

    @classmethod
    def by_id(cls, uid):
        return User.get_by_id(uid, parent=users_key())

    @classmethod
    def by_name(cls, name):
        u = User.all().filter('name =', name).get()
        return u

    @classmethod
    def register(cls, name, pw, email=None):
        pw_hash = make_pw_hash(name, pw)
        return User(parent=users_key(),
                    name=name,
                    pw_hash=pw_hash,
                    email=email)

    @classmethod
    def login(cls, name, pw):
        u = cls.by_name(name)
        if u and valid_pw(name, pw, u.pw_hash):
            return u


# blog stuff

def blog_key(name='default'):
    return db.Key.from_path('blogs', name)


class Post(db.Model):
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    user_name = db.StringProperty(required=False, default="Unknown")
    created = db.DateTimeProperty(auto_now_add=True)
    last_modified = db.DateTimeProperty(auto_now=True)
    n_likes = 0

    def render(self):

        self._render_text = self.content.replace('\n', '<br>')
        return render_str("post.html", p=self)

    def get_number_of_likes(self):
        n_likes = Like.all().filter('post_id = ', str(self.key().id())).count()
        return str(n_likes)

    def has_user_liked(self, user_name):
        prev_user_likes = Like.all().filter('user_name = ', user_name).filter(
            'post_id = ', str(self.key().id())).count()
        if (prev_user_likes > 0):
            return True
        return False

    def get_liked_users(self):
        likes = Like.all().filter('post_id = ', str(self.key().id()))
        liked_users = ""
        first_user = True
        for like in likes:
            comma = ", "
            if first_user:
                comma = ""
            liked_users = liked_users + comma + like.user_name
            first_user = False
        return liked_users

    def get_comments(self):
        return Comment.all().filter('post_id = ', str(self.key().id())).order("-created")


class Like(db.Model):
    post_id = db.StringProperty(required=True)
    user_id = db.StringProperty(required=True)


class BlogFront(BlogHandler):

    def get(self):
        posts = greetings = Post.all().order('-created')
        self.render('front.html', posts=posts)


class PostPage(BlogHandler):

    post = None

    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        self.post = db.get(key)

        if not self.post:
            self.error(404)
            return

        self.render("permalink.html", post=self.post,
                    comments=self.post.get_comments())

    def post(self, post_id):

        if not self.user:
            user_name = "Anon"
            self.redirect('/blog')
        else:
            user_name = self.user.name

        content = self.request.get('content')
        comment = Comment(
            post_id=post_id, user_name=user_name, content=content)
        comment.put()
        sleep(0.1)
        self.redirect('/blog/%s' % post_id)


class Like(db.Model):
    post_id = db.StringProperty(required=True)
    user_name = db.StringProperty(required=True)


class Comment(db.Model):
    post_id = db.StringProperty(required=True)
    user_name = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)

    def render(self):

        self._render_text = self.content.replace('\n', '<br>')
        return render_str("comment.html", comment=self)


class CreateOrEditPost(BlogHandler):

    def get(self, post_id=None):
        subject = ""
        content = ""
        if post_id:
            key = db.Key.from_path('Post', int(post_id), parent=blog_key())
            post = db.get(key)
            subject = post.subject
            content = post.content
        if self.user:
            self.render("newpost.html", subject=subject, content=content)
        else:
            self.redirect("/login")

    def post(self, post_id=None):

        if not self.user:
            self.redirect('/blog')

        subject = self.request.get('subject')
        content = self.request.get('content')

        if subject and content and self.user:
            # Edit post
            if post_id:
                key = db.Key.from_path('Post', int(post_id), parent=blog_key())
                p = db.get(key)
                p.subject = subject
                p.content = content
            # Create post
            else:
                p = Post(parent=blog_key(), subject=subject, content=content,
                         user_name=self.user.name)
            p.put()
            self.redirect('/blog/%s' % str(p.key().id()))
        else:
            error = "subject and content, please!"
            self.render(
                "newpost.html", subject=subject, content=content, error=error)


class LikePost(BlogHandler):

    def get(self, user_name=None, post_id=None):
        if post_id and user_name:
            print "YOOO I'm liking: " + str(user_name) + " " + str(post_id)
            l = Like(parent=blog_key(), post_id=post_id,
                     user_name=user_name)
            l.put()
            sleep(0.1)
            self.redirect('/blog/%s' % post_id)


class DeletePost(BlogHandler):

    def get(self, post_id):
        if post_id and self.user:
            key = db.Key.from_path('Post', int(post_id), parent=blog_key())
            p = db.get(key)
            if p.user_name == self.user.name:
                p.delete()
                sleep(0.1)
                self.redirect('/blog')


class Rot13(BlogHandler):

    def get(self):
        self.render('rot13-form.html')

    def post(self):
        rot13 = ''
        text = self.request.get('text')
        if text:
            rot13 = text.encode('rot13')

        self.render('rot13-form.html', text=rot13)


USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")


def valid_username(username):
    return username and USER_RE.match(username)

PASS_RE = re.compile(r"^.{3,20}$")


def valid_password(password):
    return password and PASS_RE.match(password)

EMAIL_RE = re.compile(r'^[\S]+@[\S]+\.[\S]+$')


def valid_email(email):
    return not email or EMAIL_RE.match(email)


class Signup(BlogHandler):

    def get(self):
        self.render("signup-form.html")

    def post(self):
        have_error = False
        self.username = self.request.get('username')
        self.password = self.request.get('password')
        self.verify = self.request.get('verify')
        self.email = self.request.get('email')

        params = dict(username=self.username,
                      email=self.email)

        if not valid_username(self.username):
            params['error_username'] = "That's not a valid username."
            have_error = True

        if not valid_password(self.password):
            params['error_password'] = "That wasn't a valid password."
            have_error = True
        elif self.password != self.verify:
            params['error_verify'] = "Your passwords didn't match."
            have_error = True

        if not valid_email(self.email):
            params['error_email'] = "That's not a valid email."
            have_error = True

        if have_error:
            self.render('signup-form.html', **params)
        else:
            self.done()

    def done(self, *a, **kw):
        raise NotImplementedError


class Unit2Signup(Signup):

    def done(self):
        self.redirect('/unit2/welcome?username=' + self.username)


class Register(Signup):

    def done(self):
        # make sure the user doesn't already exist
        u = User.by_name(self.username)
        if u:
            msg = 'That user already exists.'
            self.render('signup-form.html', error_username=msg)
        else:
            u = User.register(self.username, self.password, self.email)
            u.put()

            self.login(u)
            self.redirect('/blog')


class Login(BlogHandler):

    def get(self):
        self.render('login-form.html')

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')

        u = User.login(username, password)
        if u:
            self.login(u)
            self.redirect('/blog')
        else:
            msg = 'Invalid login'
            self.render('login-form.html', error=msg)


class Logout(BlogHandler):

    def get(self):
        self.logout()
        self.redirect('/blog')


class Unit3Welcome(BlogHandler):

    def get(self):
        if self.user:
            self.render('welcome.html', username=self.user.name)
        else:
            self.redirect('/signup')


class Welcome(BlogHandler):

    def get(self):
        username = self.request.get('username')
        if valid_username(username):
            self.render('welcome.html', username=username)
        else:
            self.redirect('/unit2/signup')

app = webapp2.WSGIApplication([('/', MainPage),
                               ('/unit2/rot13', Rot13),
                               ('/unit2/signup', Unit2Signup),
                               ('/unit2/welcome', Welcome),
                               ('/blog/?', BlogFront),
                               ('/blog/([0-9]+)', PostPage),
                               ('/blog/([0-9]+)/edit', CreateOrEditPost),
                               ('/blog/([0-9]+)/delete', DeletePost),
                               ('/blog/([0-9a-zA-Z]+)/([0-9]+)/like', LikePost),
                               ('/blog/newpost', CreateOrEditPost),
                               ('/signup', Register),
                               ('/login', Login),
                               ('/logout', Logout),
                               ('/unit3/welcome', Unit3Welcome),
                               ],
                              debug=True)
