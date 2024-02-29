from flask import Blueprint, render_template, url_for,send_file
from models.course import Course
from models.semester import Semester
from models.subject import Subject
from models.question_paper import QuestionPaper
from models.subject_semester import SubjectSemester
from models.question import Question
import base64

import io
import base64
from PIL import Image, ImageDraw


archive_bp = Blueprint('archive', __name__, template_folder='templates')

@archive_bp.route('/')
def index():
    courses = Course.query.all()
    return render_template('archive.html', courses=courses)

@archive_bp.route('/courses/<int:course_id>')
def get_semesters(course_id):
    course = Course.query.get(course_id)
    semesters = Semester.query.filter_by(CourseID=course_id).all()
    return render_template('semesters.html', course=course, semesters=semesters)

@archive_bp.route('/courses/<int:course_id>/semesters/<int:semester_id>')
def get_subjects(course_id, semester_id):
    course = Course.query.get(course_id)
    semester = Semester.query.get(semester_id)
    # Assuming SubjectSemester has a relationship with Subject
    subjects = Subject.query.join(SubjectSemester).filter(SubjectSemester.SemesterID == semester_id).all()
    return render_template('subjects.html', course=course, semester=semester, subjects=subjects)




@archive_bp.route('/courses/<int:course_id>/semesters/<int:semester_id>/subjects/<int:subject_id>/papers')
def get_question_papers(course_id, semester_id, subject_id):
    course = Course.query.get(course_id)
    semester = Semester.query.get(semester_id)
    subject = Subject.query.get(subject_id)
    question_papers = QuestionPaper.query.filter_by(SubjectID=subject_id).all()
    return render_template('question_papers.html', course=course, semester=semester, subject=subject, question_papers=question_papers)




@archive_bp.route('/courses/<int:course_id>/semesters/<int:semester_id>/subjects/<int:subject_id>/papers/<int:paper_id>')
def get_paper_details(course_id, semester_id, subject_id, paper_id):
    # Fetch paper details (including the file path)
    paper = QuestionPaper.query.get(paper_id)
    
    # Read the image file
    with Image.open(paper.FilePath) as img:
        # Define the number of strips and their height
        num_strips = 8  # Increase the number of strips for thinner strips
        strip_height = img.height // num_strips
        
        # Initialize an empty list to store strip data
        strip_data = []
        
        # Iterate over the image and extract each strip
        for i in range(num_strips):
            # Define the bounding box for the current strip
            box = (0, i * strip_height, img.width, (i + 1) * strip_height)
            
            # Crop the strip from the image
            strip_img = img.crop(box)
            
            # Convert the strip to base64 string
            buffered = io.BytesIO()
            strip_img.save(buffered, format='JPEG')
            buffered.seek(0)
            strip_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
            
            # Append the strip data to the list
            strip_data.append(strip_base64)
        
        # Ensure that the strip data list maintains the correct order
        strip_data = sorted(strip_data, key=lambda x: strip_data.index(x))
        
        # Render the template with the strip data
        return render_template('paper_details.html', strip_data=strip_data)