# app/models/question_paper.py

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, ForeignKey
from .database import db

class QuestionPaper(db.Model):
    __tablename__ = 'question_papers'
    PaperID = Column(Integer, primary_key=True, autoincrement=True)
    SubjectID = Column(Integer, ForeignKey('subjects.SubjectID'), nullable=False)
    Year = Column(Integer, nullable=False)
    ExamType = Column(String(20), nullable=False)
    FilePath = Column(String(255))