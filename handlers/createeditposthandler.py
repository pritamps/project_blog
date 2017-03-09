from bloghandler import BlogHandler
from models.post import Post

from globals import blog_key


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

        if subject and content and self.user:
            # Edit post
            if post_id:
                key = db.Key.from_path('Post', int(post_id), parent=blog_key())
                p = db.get(key)
                p.subject = subject
                p.content = content
                title = "edit post"
            # Create post
            else:
                title = "new post"
                p = Post(parent=blog_key(), title=title, subject=subject,
                         content=content, user_name=self.user.name)
            p.put()
            self.redirect('/blog/%s' % str(p.key().id()))
        else:
            error = "subject and content, please!"
            self.render("createoreditpost.html", subject=subject,
                        content=content, error=error)