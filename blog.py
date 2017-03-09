import webapp2

from models.comment import Comment
from models.post import Post
from models.user import User
from models.like import Like

from handlers.bloghandler import BlogHandler
from handlers.mainpagehandler import MainPage
from handlers.blogfronthandler import BlogFront
from handlers.postpagehandler import PostPage
from handlers.posthandlers import CreateOrEditPost, DeletePost, LikePost
from handlers.commenthandlers import CreateEditComment, DeleteComment
from handlers.signup import Signup, Register
from handlers.loginlogout import Login, Logout


from globals import template_dir, jinja_env, secret, render_str, blog_key


app = webapp2.WSGIApplication([('/', MainPage),
                               ('/blog/?', BlogFront),
                               ('/blog/([0-9]+)', PostPage),
                               ('/blog/([0-9]+)/edit', CreateOrEditPost),
                               ('/blog/([0-9]+)/comment', CreateEditComment),
                               ('/blog/([0-9]+)/([0-9]+)/edit', CreateEditComment),
                               ('/blog/([0-9]+)/([0-9]+)/delete',
                                DeleteComment),
                               ('/blog/([0-9]+)/delete', DeletePost),
                               ('/blog/([0-9a-zA-Z]+)/([0-9]+)/like',
                                LikePost),
                               ('/blog/newpost', CreateOrEditPost),
                               ('/signup', Register),
                               ('/login', Login),
                               ('/logout', Logout)
                               ],
                              debug=True)
