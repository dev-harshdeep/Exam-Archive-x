# app/models/semester.py

from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint, Text
from .database import db

class Semester(db.Model):
    __tablename__ = 'semesters'
    SemesterID = Column(Integer, primary_key=True, autoincrement=True)
    CourseID = Column(Integer, ForeignKey('courses.CourseID'), nullable=False)
    SemesterName = Column(String(255), nullable=False)
    UniqueConstraint('CourseID', 'SemesterName', name='uq_semesters_course_semester')
