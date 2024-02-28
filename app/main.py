from flask import Flask, render_template, jsonify
from views.home import home_bp
from views.auth import auth_bp
from views.admin import admin_bp
from views.data import data_bp
from views.pdfUpload import pdf_upload_bp
from views.archive import archive_bp
from views.search import search_bp
from dotenv import load_dotenv
from models.database import db
from models.course import Course
from sqlalchemy import inspect
from models.course import Course
from models.semester import Semester
from models.subject import Subject
from models.question_paper import QuestionPaper
from models.question import Question
from config import Config
from data_loader import load_data 

load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
app.register_blueprint(home_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(data_bp, url_prefix='/data')
app.register_blueprint(pdf_upload_bp)
app.register_blueprint(archive_bp, url_prefix='/archive')
app.register_blueprint(search_bp)

# Function to check if tables exist in the 
def tables_exist():
    with app.app_context():
        inspector = inspect(db.engine)
        return all(table in inspector.get_table_names() for table in ['courses', 'semesters', 'subjects', 'question_papers', 'questions'])

# Function to check if there is any data in the tables
def data_exists():
    with app.app_context():
        return any(db.session.query(model).count() > 0 for model in [Course, Semester, Subject, QuestionPaper, Question])
    
# Create all tables and load data if necessary
if not tables_exist():
    with app.app_context():
        db.create_all()


#Fill tabls if no data exist in the created tables
if not data_exists():
    with app.app_context():
        json_file_path = 'output.json'  # Change this to your JSON file path
        load_data(json_file_path)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
