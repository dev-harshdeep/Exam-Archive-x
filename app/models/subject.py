# app/models/subject.py

from flask_sqlalchemy import SQLAlchemy

from .database import db

class Subject(db.Model):
    __tablename__ = 'Subjects'
    SubjectID = db.Column(db.Integer, primary_key=True)
    SemesterID = db.Column(db.Integer, db.ForeignKey('Semesters.SemesterID'), nullable=False)
    Code = db.Column(db.String(10), nullable=False)
    SubjectName = db.Column(db.String(255), nullable=False)
