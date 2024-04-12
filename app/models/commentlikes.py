from .database import db
from sqlalchemy import Column, Integer, ForeignKey, Boolean

class Commentlikes(db.Model):
    __tablename__ = 'commentlikes'

    LikeDislikeID = Column(Integer, primary_key=True, autoincrement=True)
    UserID = Column(Integer, ForeignKey('users.id'))  # Assuming you have a users table
    PostID = Column(Integer, ForeignKey('comments.CommentID'))
    Action = Column(Integer)  # True for like, False for dislike
