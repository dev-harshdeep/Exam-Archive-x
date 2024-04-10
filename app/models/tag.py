from .database import db
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean

class Tag(db.Model):
    __tablename__ = 'tags'
    TagID = Column(Integer, primary_key=True, autoincrement=True)
    TagName = Column(String(255), nullable=False, unique=True)  # Assuming tag names are unique

    def __init__(self, TagName):
        self.TagName = TagName
