from .database import db
from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint, Column, Integer, String, ForeignKey, DateTime, Text, Boolean

class CategoryPost(db.Model):
    __tablename__ = 'category_post'
    CategoryPostID = Column(Integer, autoincrement=True ,primary_key = True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.CategoryID'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.PostID'))

    # Define a composite unique constraint for category_id and post_id
    __table_args__ = (
        UniqueConstraint('category_id', 'post_id', name='unique_category_post'),
    )

    def __init__(self, category_id, post_id):
        self.category_id = category_id
        self.post_id = post_id
