from time import sleep

from bloghandler import BlogHandler
from models.post import Post

from google.appengine.ext import db

from models.comment import Comment

from globals import blog_key


class PostPage(BlogHandler):
    """Handler for the display of a post"""

    post_obj = None

    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        self.post_obj = db.get(key)

        if not self.post_obj:
            self.error(404)
            return

        self.render("permalink.html", post=self.post_obj,
                    comments=self.post_obj.get_comments())

    def post(self, post_id):
        """
        Adds a new comment to the post
        """
        content = self.request.get('content')

        if not content:
            self.redirect('/blog/%s' % post_id)
            return
        if not self.user:
            user_name = "Anon"
            # self.redirect('/blog')
        else:
            user_name = self.user.name

        comment = Comment(parent=blog_key(), post_id=post_id,
                          user_name=user_name, content=content)
        comment.put()
        sleep(0.1)
        self.redirect('/blog/%s' % post_id)
