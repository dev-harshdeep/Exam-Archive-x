from flask import Flask
from views.home import home_bp
from views.auth import auth_bp
from views.admin import admin_bp
from flask_sqlalchemy import SQLAlchemy
from google_auth_oauthlib.flow import Flow
import os
from dotenv import load_dotenv
from models.database import db
from models.course import Course 

load_dotenv()

# app = Flask(__name__)
# # app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://dev:1234@db/courseinfo'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.secret_key = "ExamArchive.com"
# os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

# Initialize the main db instance
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@db:5432/courseinfo'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "ExamArchive.com"
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

# Initialize the main db instance
db.init_app(app)

@app.route('/show')
def display_courses():
    all_courses = Course.query.all()
    for course in all_courses:
        print(f"Course ID: {course.CourseID}, Course Name: {course.CourseName}")
    return "Check the console for course information."

# Register blueprints
app.register_blueprint(home_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp, url_prefix='/admin')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
