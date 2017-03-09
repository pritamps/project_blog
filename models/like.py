from google.appengine.ext import db


class Like(db.Model):
    """
    GQL DB model for likes on a Post
    """
    post_id = db.StringProperty(required=True)
    user_name = db.StringProperty(required=True)