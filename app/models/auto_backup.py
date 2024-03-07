# app/models/auto_backup.py

from flask_sqlalchemy import SQLAlchemy
from .database import db

class AutoBackupSettings(db.Model):
    __tablename__ = 'auto_backup_settings'
    id = db.Column(db.Integer, primary_key=True)
    time_frame = db.Column(db.String(20), nullable=False)
    frequency = db.Column(db.Integer, nullable=False)
    enabled = db.Column(db.Boolean, default=False, nullable=False)
