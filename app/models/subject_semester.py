# app/models/subject_semester.py

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, ForeignKey
from .database import db

class SubjectSemester(db.Model):
    __tablename__ = 'subject_semester'
    id = Column(Integer, primary_key=True, autoincrement=True)
    SubjectID = Column(Integer, ForeignKey('subjects.SubjectID'), nullable=False)
    SemesterID = Column(Integer, ForeignKey('semesters.SemesterID'), nullable=False)

