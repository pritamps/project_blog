from google.appengine.ext import db
import globals


class Comment(db.Model):
    """
    GQL DB model for comments on a Post
    """
    post_id = db.StringProperty(required=True)
    user_name = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)

    def render(self):

        self._render_text = self.content.replace('\n', '<br>')
        return globals.render_str("comment.html", comment=self)
