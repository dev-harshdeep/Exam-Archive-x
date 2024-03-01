import math
import os
from flask import Blueprint, render_template, session, redirect
from models.question_paper import QuestionPaper
from views.auth import login_is_required
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

def get_last_backup_date():
    # Suppose you retrieve the last backup date from a database
    return datetime(2023, 5, 20, 15, 30, 0)  # Example date and time

@admin_bp.route('/dashboard')
@login_is_required
def dashboard():
    # Query the database to count the number of question papers
    num_papers = QuestionPaper.query.count()

    # Get the size of the folder where question papers are stored
    folder_path =  os.path.join('/app/paperFiles')
    folder_size = get_folder_size(folder_path)

    # Convert folder size to a human-readable format (e.g., KB, MB, GB)
    folder_size_gb =round( folder_size / (1024 * 1024 ),2)  # Convert bytes to MB

    return render_template('admin/dashboard.html', num_papers=num_papers, folder_size_gb=folder_size_gb , last_backup_date=get_last_backup_date())

def get_folder_size(folder_path):
    # Get the size of the specified folder
    folder_size = 0
    for dirpath, _, filenames in os.walk(folder_path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            folder_size += os.path.getsize(file_path)
        break  # We only need the size of the immediate folder, so break after the first iteration
    return folder_size
@admin_bp.route('/edit-course-info')
@login_is_required
def edit_course_info():    
    return "Edit Course Info Page"

@admin_bp.route('/add-question-paper')
@login_is_required
def add_question_paper():
    return "Add Question Paper Page"
