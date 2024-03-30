# utils/email.py

from flask_mail import Mail, Message
from flask import current_app

mail = Mail()

def send_verification_email(to, verification_link):
    msg = Message(subject='Email Verification', recipients=[to])
    msg.body = f'Please click the following link to verify your email: {verification_link}'
    mail.send(msg)
