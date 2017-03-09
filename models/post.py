from google.appengine.ext import db
from globals import render_str
from comment import Comment
from like import Like


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
        """ Returns number of likes that the current post has """
        n_likes = Like.all().filter('post_id = ', str(self.key().id())).count()
        return str(n_likes)

    def has_user_liked(self, user_name):
        """ Returns if the current user has liked this post """
        prev_user_likes = Like.all().filter('user_name = ', user_name).filter(
            'post_id = ', str(self.key().id())).count()
        if (prev_user_likes > 0):
            return True
        return False

    def get_liked_users(self):
        """ Returns list of users for the popup """
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
        """ Returns comments associated with this post """
        return Comment.all().filter('post_id = ', str(self.key().id())).order("-created")