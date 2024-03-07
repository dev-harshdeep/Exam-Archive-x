import os
import json
import tarfile
from datetime import datetime
import shutil
from flask import current_app , app
from datetime import datetime
from models.course import Course
from models.question_paper import QuestionPaper
from models.question import Question
from models.semester import Semester
from models.subject_semester import SubjectSemester
from models.subject import Subject
from sqlalchemy import  MetaData

def serialize_object(obj):
    """Serialize SQLAlchemy object to dictionary."""
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}

def backup_database_and_files():

    current_app.logger.info("Starting backup")
    try:
        # Create backup directory
        backup_dir = '/app/backupFiles'
        os.makedirs(backup_dir, exist_ok=True)

        # Backup database tables to JSON files
        backup_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_subdir = os.path.join(backup_dir, f"backup_{backup_timestamp}")
        os.makedirs(backup_subdir)

        for Model, filename in [(Course, 'courses.json'), 
                                (QuestionPaper, 'question_papers.json'), 
                                (Question, 'questions.json'), 
                                (Semester, 'semesters.json'), 
                                (SubjectSemester, 'subject_semesters.json'), 
                                (Subject, 'subjects.json')]:
            data = [serialize_object(instance) for instance in Model.query.all()]
            with open(os.path.join(backup_subdir, filename), 'w') as f:
                json.dump(data, f, indent=4)
        current_app.logger.info("Database backup files created")

        # Backup paperFiles directory
        paper_files_dir = '/app/paperFiles'
        paper_files_backup_dir = os.path.join(backup_subdir, 'paperFiles')
        shutil.copytree(paper_files_dir, paper_files_backup_dir)
        current_app.logger.info("Paper files backup created")

        # Create TAR archive
        tar_filename = f'backup_{backup_timestamp}.tar.gz'
        tar_path = os.path.join(backup_dir, tar_filename)
        with tarfile.open(tar_path, "w:gz") as tar:
            tar.add(backup_subdir, arcname=os.path.basename(backup_subdir))

        current_app.logger.info("Backup file successfully created")

        # Clean up: remove the backup directory
        shutil.rmtree(backup_subdir)

    except Exception as e:
        current_app.logger.info(f"Error: {str(e)}")
