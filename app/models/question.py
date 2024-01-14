# app/models/question.py

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint, Text
from .database import db

class Question(db.Model):
    __tablename__ = 'questions'
    QuestionID = Column(Integer, primary_key=True, autoincrement=True)
    PaperID = Column(Integer, ForeignKey('question_papers.PaperID'), nullable=False)
    QuestionNumber = Column(Integer, nullable=False)
    Coordinates = Column(String(50))
    MetaText = Column(Text)
    UniqueConstraint('PaperID', 'QuestionNumber', name='uq_questions_paper_question')   