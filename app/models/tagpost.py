from .database import db
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean


class TagPost(db.Model):
    __tablename__ = 'tag_post'
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.TagID'), primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.PostID'), primary_key=True)

    def __init__(self, tag_id, post_id):
        self.tag_id = tag_id
        self.post_id = post_id
