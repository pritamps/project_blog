from time import sleep

from bloghandler import BlogHandler
from models.like import Like

from globals import blog_key


class LikePost(BlogHandler):
    """ Handler that handles liking a post """

    def get(self, user_name=None, post_id=None):
        if post_id and user_name:
            l = Like(parent=blog_key(), post_id=post_id,
                     user_name=user_name)
            l.put()
            sleep(0.1)
            self.redirect('/blog/%s' % post_id)
