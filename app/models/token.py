# app/models/token.py

from .database import db

class Token(db.Model):
    __tablename__ = 'tokens'
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(256), unique=True, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)

    def __init__(self, token, user_id, created_at, expires_at):
        self.token = token
        self.user_id = user_id
        self.created_at = created_at
        self.expires_at = expires_at
