from time import sleep

from bloghandler import BlogHandler
from models.post import Post
from models.like import Like

from google.appengine.ext import db

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


class DeletePost(BlogHandler):
    """
    Deletes a Post
    """

    def get(self, post_id):
        if post_id and self.user:
            key = db.Key.from_path('Post', int(post_id), parent=blog_key())
            p = db.get(key)
            if not p:
                self.error(404)
                return
            if p.user.name == self.user.name:
                p.delete()
                sleep(0.1)
                self.redirect('/blog')
        else:
            self.error(404)
            return


class CreateOrEditPost(BlogHandler):
    """
    Handler for creating new posts and editing existing ones
    """

    def get(self, post_id=None):
        subject = ""
        content = ""
        title = "new post"
        if post_id:
            key = db.Key.from_path('Post', int(post_id), parent=blog_key())
            post = db.get(key)
            subject = post.subject
            content = post.content
            title = "edit post"
        if self.user:
            self.render("createoreditpost.html", title=title,
                        subject=subject, content=content)
        else:
            self.redirect("/login")

    def post(self, post_id=None):
        """ Handles post request (clicking the Submit button)"""

        if not self.user:
            self.redirect('/blog')

        subject = self.request.get('subject')
        content = self.request.get('content')

        if subject and content:
            # Edit post
            if post_id:
                key = db.Key.from_path('Post', int(post_id), parent=blog_key())
                p = db.get(key)
                if not p:
                    self.error(404)
                    return
                p.subject = subject
                p.content = content
                title = "edit post"
            # Create post
            else:
                title = "new post"
                p = Post(parent=blog_key(), title=title, subject=subject,
                         content=content, user=self.user)
            p.put()
            self.redirect('/blog/%s' % str(p.key().id()))
        else:
            error = "subject and content, please!"
            self.render("createoreditpost.html", subject=subject,
                        content=content, error=error)
