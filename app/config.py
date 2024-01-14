import os

os.environ["GOOGLE_CLIENT_ID"] = "1021957323011-mhbqnueds5ju8mvk1pala345f43arai8.apps.googleusercontent.com"
os.environ["CLIENT_SECRETS_FILE"] = "secrets/client_secret.json"

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'mysql+pymysql://user:password@db:3306/courseInfo')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "ExamArchive.com"
