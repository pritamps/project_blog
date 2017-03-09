from bloghandler import BlogHandler
from time import sleep

from models.post import Post
from globals import blog_key

from google.appengine.ext import db


class DeletePost(BlogHandler):
    """
    Deletes a Post
    """

    def get(self, post_id):
        if post_id and self.user:
            key = db.Key.from_path('Post', int(post_id), parent=blog_key())
            p = db.get(key)
            if p.user_name == self.user.name:
                p.delete()
                sleep(0.1)
                self.redirect('/blog')
