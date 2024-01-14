# app/models/course.py

from flask_sqlalchemy import SQLAlchemy
from .database import db


class Course(db.Model):
    __tablename__ = 'courses'
    CourseID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    CourseName = db.Column(db.String(255))
