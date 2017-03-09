from time import sleep
from bloghandler import BlogHandler
from google.appengine.ext import db

from models.post import Post
from models.comment import Comment

from globals import blog_key


class CreateComment(BlogHandler):
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


class DeleteComment(BlogHandler):
    """
    Deletes a Comment
    """

    def get(self, post_id, comment_id):
        if post_id and comment_id and self.user:
            print "YOOOO "
            key = db.Key.from_path('Comment', int(
                comment_id), parent=blog_key())
            c = db.get(key)
            if c.user_name == self.user.name:

                c.delete()
                sleep(0.1)
                self.redirect('/blog/%s' % post_id)


class EditComment(BlogHandler):
    """
    Edits Comment
    """

    def get(self, post_id, comment_id):
        if post_id and comment_id and self.user:
            key = db.Key.from_path('Comment', int(
                comment_id), parent=blog_key())
            c = db.get(key)
            content = c.content
            self.render("editcomment.html", content=content)

    def post(self, post_id=None, comment_id=None):
        """ Handles post request (clicking the Submit button)"""

        if not self.user:
            self.redirect('/blog')

        content = self.request.get('content')

        if content and self.user:
            if comment_id:
                key = db.Key.from_path('Comment', int(
                    comment_id), parent=blog_key())
                c = db.get(key)
                c.content = content
                c.put()
                self.redirect('/blog/%s' % str(c.post_id))
        else:
            error = "content, please!"
            self.render(
                "createoreditpost.html", content=content, error=error)