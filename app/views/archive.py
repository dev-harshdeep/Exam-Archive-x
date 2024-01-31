# blueprints/traversal.py

from flask import Blueprint, jsonify, render_template
from models.course import Course
from models.semester import Semester
from models.subject import Subject

traversal_bp = Blueprint('traversal', __name__)

@traversal_bp.route('/courses', methods=['GET'])
def get_courses():
    courses = Course.query.all()
    courses_data = [{'id': course.CourseID, 'name': course.CourseName} for course in courses]
    return jsonify({'courses': courses_data})

@traversal_bp.route('/semesters/<int:course_id>', methods=['GET'])
def get_semesters(course_id):
    semesters = Semester.query.filter_by(CourseID=course_id).all()
    semester_data = [{'id': semester.SemesterID, 'name': semester.SemesterName} for semester in semesters]
    return jsonify({'semesters': semester_data})

@traversal_bp.route('/subjects/<int:semester_id>', methods=['GET'])
def get_subjects(semester_id):
    subjects = Subject.query.filter_by(SemesterID=semester_id).all()
    subject_data = [{'id': subject.SubjectID, 'code': subject.Code, 'name': subject.SubjectName} for subject in subjects]
    return jsonify({'subjects': subject_data})

@traversal_bp.route('/', methods=['GET'])
def index():
    return render_template('archive.html')
