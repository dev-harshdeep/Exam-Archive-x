from flask import Flask, render_template, jsonify
from views.home import home_bp
from views.auth import auth_bp
from views.admin import admin_bp
from views.data import data_bp
from views.pdfUpload import pdf_upload_bp
from views.archive import archive_bp
from views.search import search_bp
from views.editCourse import edit_course_bp
from views.status import status_bp
from views.autoBackup import auto_backup_bp
from dotenv import load_dotenv
from models.database import db
from models.course import Course
from sqlalchemy import inspect
from models.course import Course
from models.semester import Semester
from models.subject import Subject
from models.question_paper import QuestionPaper
from models.question import Question
from models.auto_backup import AutoBackupSettings
from config import Config
from data_loader import load_data 
from views.autoBackup import schedule_initial_backup_job
from models.cache import cache


load_dotenv()

app = Flask(__name__)
cache.init_app(app, config={'CACHE_TYPE': 'SimpleCache'})
app.config.from_object(Config)
db.init_app(app)
app.register_blueprint(home_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(data_bp, url_prefix='/data')
app.register_blueprint(pdf_upload_bp)
app.register_blueprint(archive_bp, url_prefix='/archive')

app.register_blueprint(edit_course_bp, url_prefix='/editCourse')
app.register_blueprint(search_bp)

app.register_blueprint(status_bp)
app.register_blueprint(auto_backup_bp)


# Function to check if tables exist in the 
def tables_exist():
    with app.app_context():
        inspector = inspect(db.engine)
        return all(table in inspector.get_table_names() for table in ['courses', 'semesters', 'subjects', 'question_papers', 'questions','auto_backup_settings' ])

# Function to check if there is any data in the tables
def data_exists():
    with app.app_context():
        return any(db.session.query(model).count() > 0 for model in [Course, Semester, Subject, QuestionPaper, Question ,AutoBackupSettings])
    
# Create all tables and load data if necessary
if not tables_exist():
    with app.app_context():
        db.create_all()


#Fill tabls if no data exist in the created tables
# if not data_exists():
#     with app.app_context():
#         json_file_path = 'output.json'  # Change this to your JSON file path
#         load_data(json_file_path)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

with app.app_context():

    # Set up any initial configurations or tasks here
    schedule_initial_backup_job()



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
