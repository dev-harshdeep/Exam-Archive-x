from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean
from .database import db


class Comments(db.Model):
    __tablename__ = 'comments'
     
    CommentID = Column(Integer, autoincrement=True ,primary_key = True)  # Assuming CommentID references the comments table
    ThreadId = Column(Integer, ForeignKey('threads.ThreadID'), nullable=False)
    UserID = Column(Integer, ForeignKey('users.id'), nullable=False)
    Content = Column(Text, nullable=False)
    TimeStamp = Column(DateTime, nullable=False)
    Reply = Column(Integer, ForeignKey('comments.CommentID'))  # Assuming it refers to the parent thread
    Likes = Column(Integer, default=0)
