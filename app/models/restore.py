import os
import json
import tarfile
import shutil
from flask import current_app
from models.database import db  # Import the db object
from models.course import Course
from models.question_paper import QuestionPaper
from models.question import Question
from models.semester import Semester
from models.subject_semester import SubjectSemester
from models.subject import Subject

# Define restoration functions for each table
def restore_courses(backup_dir):
    with open(os.path.join(backup_dir, 'courses.json'), 'r') as f:
        courses_data = json.load(f)
        for course_data in courses_data:
            course = Course(**course_data)
            db.session.add(course)
        db.session.commit()

def restore_question_papers(backup_dir):
    with open(os.path.join(backup_dir, 'question_papers.json'), 'r') as f:
        question_papers_data = json.load(f)
        for question_paper_data in question_papers_data:
            question_paper = QuestionPaper(**question_paper_data)
            db.session.add(question_paper)
        db.session.commit()

def restore_questions(backup_dir):
    with open(os.path.join(backup_dir, 'questions.json'), 'r') as f:
        questions_data = json.load(f)
        for question_data in questions_data:
            question = Question(**question_data)
            db.session.add(question)
        db.session.commit()

def restore_semesters(backup_dir):
    with open(os.path.join(backup_dir, 'semesters.json'), 'r') as f:
        semesters_data = json.load(f)
        for semester_data in semesters_data:
            semester = Semester(**semester_data)
            db.session.add(semester)
        db.session.commit()

def restore_subject_semesters(backup_dir):
    with open(os.path.join(backup_dir, 'subject_semesters.json'), 'r') as f:
        subject_semesters_data = json.load(f)
        for subject_semester_data in subject_semesters_data:
            subject_semester = SubjectSemester(**subject_semester_data)
            db.session.add(subject_semester)
        db.session.commit()

def restore_subjects(backup_dir):
    with open(os.path.join(backup_dir, 'subjects.json'), 'r') as f:
        subjects_data = json.load(f)
        for subject_data in subjects_data:
            subject = Subject(**subject_data)
            db.session.add(subject)
        db.session.commit()

# Define the function to restore the backup
def restore_backup(backup_path):
    try:
        # Extract backup archive
        with tarfile.open(backup_path, "r:gz") as tar:
            backup_dir = os.path.join('/tmp', tar.getnames()[0])  # Get the extracted directory name
            tar.extractall(path='/tmp')
        db.session.query(Question).delete()
        db.session.query(QuestionPaper).delete()
        db.session.query(SubjectSemester).delete()
        db.session.query(Subject).delete()
        db.session.query(Semester).delete()
        db.session.query(Course).delete()
        db.session.commit()
        # Restore each table from respective JSON files
        restore_courses(backup_dir)
        restore_semesters(backup_dir)
        restore_subjects(backup_dir)
        restore_subject_semesters(backup_dir)
        restore_question_papers(backup_dir)
        restore_questions(backup_dir)

        paper_files_src = os.path.join(backup_dir, 'paperFiles')
        paper_files_dest = '/app/paperFiles'
       
        os.makedirs(paper_files_dest, exist_ok=True)  # Recreate the directory if it doesn't exist
        for root, _, files in os.walk(paper_files_src):
            for file in files:
                shutil.copy(os.path.join(root, file), paper_files_dest)


        return True  

    except Exception as e:
        current_app.logger.error(f"Error: {str(e)}")
        return False
