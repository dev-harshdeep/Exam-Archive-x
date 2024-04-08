from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean
from .database import db

class Post(db.Model):
    __tablename__ = 'posts'
    PostID = Column(Integer, primary_key=True, autoincrement=True)
    UserID = Column(Integer, ForeignKey('users.id'), nullable=False)  # Assuming there's a users table
    Content = Column(Text, nullable=False)  # Store markdown content as Text
    TimeStamp = Column(DateTime, nullable=False)
    DifficultyLevel = Column(Integer, nullable=False)  # Adjust the type as needed
    Streams = Column(String(255))  # Assuming streams are comma-separated or you can normalize it further
    Tags = Column(String(255))  # Assuming tags are comma-separated or you can normalize it further
    Approved = Column(Integer, default=0)  # New attribute: Whether the post is approved or not
    ApprovedBy = Column(Integer, ForeignKey('users.id'))  # New attribute: User ID of the approver

    def __init__(self, UserID, Content, TimeStamp, DifficultyLevel, Streams="", Tags="", Approved=0, ApprovedBy=None):
        self.UserID = UserID
        self.Content = Content
        self.TimeStamp = TimeStamp
        self.DifficultyLevel = DifficultyLevel
        self.Streams = Streams
        self.Tags = Tags
        self.Approved = Approved
        self.ApprovedBy = ApprovedBy
