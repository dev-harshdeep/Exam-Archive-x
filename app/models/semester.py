# app/models/semester.py

from flask_sqlalchemy import SQLAlchemy

from .database import db

class Semester(db.Model):
    __tablename__ = 'Semesters'
    SemesterID = db.Column(db.Integer, primary_key=True)
    CourseID = db.Column(db.Integer, db.ForeignKey('Courses.CourseID'), nullable=False)
    SemesterName = db.Column(db.String(255), nullable=False)
