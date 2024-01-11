# app/models/question_paper.py

from flask_sqlalchemy import SQLAlchemy

from .database import db

class QuestionPaper(db.Model):
    __tablename__ = 'QuestionPapers'
    PaperID = db.Column(db.Integer, primary_key=True)
    SubjectID = db.Column(db.Integer, db.ForeignKey('Subjects.SubjectID'), nullable=False)
    Year = db.Column(db.Integer, nullable=False)
    ExamType = db.Column(db.String(20), nullable=False)
    FilePath = db.Column(db.String(255))
