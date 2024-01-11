# app/models/course.py

from flask_sqlalchemy import SQLAlchemy
from .database import db


class Course(db.Model):
    __tablename__ = 'Courses'
    CourseID = db.Column(db.Integer, primary_key=True)
    CourseName = db.Column(db.String(255), nullable=False)
