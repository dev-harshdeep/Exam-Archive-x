from .database import db
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean


class Category(db.Model):
    __tablename__ = 'categories'
    CategoryID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    CategoryName = db.Column(db.String(255), nullable=False, unique=True)

    def __init__(self, CategoryName):
        self.CategoryName = CategoryName
