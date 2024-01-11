# app/admin.py

from flask import Blueprint, render_template, session , redirect
from views.auth import login_is_required  # Import the login_is_required decorator
from views.auth import Authorised  # Make sure to import Authorised
from functools import wraps

admin_bp = Blueprint('admin', __name__)

# def login_is_required_admin(function):
#     @wraps(function)
#     def wrapper(*args, **kwargs):
#         if "google_id" in session and "google_token" in session:
#             if session["email"] in Authorised:
                
#                 return function()
#         return redirect("/logout")
#     return wrapper

@admin_bp.route('/dashboard')
@login_is_required
def dashboard():
    # if session.get('email') == 'admin@example.com':
    return render_template('admin/dashboard.html')
    # else:
    #     return "You do not have permission to access the admin dashboard."

@admin_bp.route('/edit-course-info')
@login_is_required
def edit_course_info():    
    return "Edit Course Info Page"

@admin_bp.route('/add-question-paper')
@login_is_required
def add_question_paper():
    return "Add Question Paper Page"
