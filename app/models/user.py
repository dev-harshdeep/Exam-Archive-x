# app/models/user.py

from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from werkzeug.security import generate_password_hash, check_password_hash

from .database import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    email_verified = db.Column(db.Boolean, default=False) 
    
    # Admin fields
    is_admin = db.Column(db.Boolean, default=False)
    admin_role_id = db.Column(db.Integer, db.ForeignKey('admin_roles.id'))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, salt_length=16)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class AdminRole(db.Model):
    __tablename__ = 'admin_roles'
    id = db.Column(db.Integer, primary_key=True)
    can_access_backup = db.Column(db.Boolean, default=False)
    can_edit_posts = db.Column(db.Boolean, default=False)
    can_edit_courses = db.Column(db.Boolean, default=False)
    can_upload_pdfs = db.Column(db.Boolean, default=False)
    can_manage_admins = db.Column(db.Boolean, default=False)
