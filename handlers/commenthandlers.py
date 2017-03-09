from time import sleep
from bloghandler import BlogHandler
from google.appengine.ext import db

from models.post import Post
from models.comment import Comment

from globals import blog_key


class CreateEditComment(BlogHandler):

    def get(self, post_id, comment_id):
        if post_id and comment_id and self.user:
            key = db.Key.from_path('Comment', int(
                comment_id), parent=blog_key())
            c = db.get(key)

            if not c:
                self.error(404)
                return

            self.render('editcomment.html', content=c.content)

    def post(self, post_id, comment_id=None):
        """
        Adds a new comment to the post
        """
        content = self.request.get('content')

        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)

        if not post:
            self.error(404)
            return

        if not self.user:
            user_name = "Anon"
            # self.redirect('/blog')
        else:
            user_name = self.user.name

        if not content:
            self.render("permalink.html", post=post, comments=post.comments,
                        user=self.user,
                        error_comment="No text provided for comment")
            return
        # Create comment
        if not comment_id:
            comment = Comment(parent=blog_key(), post=post,
                              user_name=user_name, content=content)
        # Edit comment
        else:
            key = db.Key.from_path('Comment', int(comment_id),
                                   parent=blog_key())
            comment = db.get(key)
            if not comment:
                self.error(404)
                return
            # Make sure comment author is same as current user before
            # making the edit. If there is a mismatch, redirect to post page
            if not (self.comment.user_name == self.user.name):
                self.redirect('/blog/%s' % post_id)
                return
            comment.content = content
        comment.put()
        sleep(0.1)
        self.redirect('/blog/%s' % post_id)


class DeleteComment(BlogHandler):
    """
    Deletes a Comment
    """

    def get(self, post_id, comment_id):
        if post_id and comment_id and self.user:
            key = db.Key.from_path('Comment', int(
                comment_id), parent=blog_key())
            c = db.get(key)

            if c and c.user_name == self.user.name:

                c.delete()
                sleep(0.1)
                self.redirect('/blog/%s' % post_id)
            else:
                self.error(404)
                return
        else:
            self.error(404)
            return


class EditComment(BlogHandler):
    """
    Edits Comment
    """

