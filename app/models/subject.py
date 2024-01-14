# app/models/subject.py

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint, Text

from .database import db

class Subject(db.Model):
    __tablename__ = 'subjects'
    SubjectID = Column(Integer, primary_key=True, autoincrement=True)
    SemesterID = Column(Integer, ForeignKey('semesters.SemesterID'), nullable=False)
    Code = Column(String(10), nullable=False)
    SubjectName = Column(String(255), nullable=False)
    UniqueConstraint('SemesterID', 'Code', name='uq_subjects_semester_code')