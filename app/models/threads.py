

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean
from .database import db


class Thread(db.Model):
    __tablename__ = 'threads'

    ThreadID = Column(Integer, primary_key=True, autoincrement=True)
    PostID = Column(Integer, ForeignKey('posts.PostID'))
    IsLock = Column(Boolean , default=False) 
    


