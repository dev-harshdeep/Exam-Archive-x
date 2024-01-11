# app/models/question.py

from flask_sqlalchemy import SQLAlchemy

from .database import db

class Question(db.Model):
    __tablename__ = 'Questions'
    QuestionID = db.Column(db.Integer, primary_key=True)
    PaperID = db.Column(db.Integer, db.ForeignKey('QuestionPapers.PaperID'), nullable=False)
    QuestionNumber = db.Column(db.Integer, nullable=False)
    Coordinates = db.Column(db.String(50))
    MetaText = db.Column(db.Text)
