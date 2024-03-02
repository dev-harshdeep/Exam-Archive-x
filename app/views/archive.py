from flask import Blueprint, render_template, url_for,send_file , redirect ,current_app ,request
from models.course import Course
from models.semester import Semester
from models.subject import Subject
from models.question_paper import QuestionPaper
from models.subject_semester import SubjectSemester
from models.question import Question
import base64
from urllib.parse import unquote
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


def get_question_start_position(question_number):
    # Query the database to get the question based on the question number
    question = Question.query.filter_by(QuestionNumber=question_number).first()
    if question:
        # Parse the coordinates to get the start position
        coordinates = question.Coordinates.split('-')
        if len(coordinates) == 2:
            start_position = int(coordinates[0])
            return start_position
    return None

# In your backend route handler

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
        
        # Calculate the aspect ratio of the original image
        aspect_ratio = img.width / img.height
        start_position=1
        # Check if question number is present in the URL
        question_number = request.args.get('question_number')
        if int(question_number) in range(1,6):
            # Get the start position of the question
            start_position = get_question_start_position(question_number)
            if start_position:
                # Calculate the scroll height based on the start position and aspect ratio
                scroll_height = (start_position / aspect_ratio) * strip_height
            else:
                scroll_height = 0
        else:
            scroll_height = 0
        
        # Render the template with the strip data and scroll height
        return render_template('paper_details.html', strip_data=strip_data, scroll_height=scroll_height, scrollV=img.height/start_position , aspect_ratio = aspect_ratio)


@archive_bp.route('/papers/<string:paper_code>/<string:exam_type>/<int:exam_year>/<int:question_number>')
def redirect_to_paper_by_code(paper_code, exam_type, exam_year, question_number):
    # Decode the paper code
    decoded_paper_code = unquote(paper_code)

    # Query the Subject table to get the SubjectID based on the provided subject code
    subject = Subject.query.filter_by(Code=decoded_paper_code).first()
    if subject:
        # Query the SubjectSemester table to find the first instance where the SubjectID appears
        subject_semester = SubjectSemester.query.filter_by(SubjectID=subject.SubjectID).first()
        if subject_semester:
            # Retrieve the SemesterID
            semester_id = subject_semester.SemesterID
            
            # Query the Semester table to get the CourseID
            semester = Semester.query.get(semester_id)
            if semester:
                # Query the QuestionPaper table to get the paper ID based on the provided information
                paper = QuestionPaper.query.filter_by(SubjectID=subject.SubjectID,
                                                        ExamType=exam_type,
                                                        Year=exam_year).first()
                if paper:
                    # Construct the URL for the paper details page
                    redirect_url = url_for('archive.get_paper_details',
                                           course_id=semester.CourseID,
                                           semester_id=semester_id,
                                           subject_id=subject.SubjectID,
                                           paper_id=paper.PaperID,
                                           question_number=question_number)
                    
                    # Redirect to the paper details page
                    return redirect(redirect_url)
    
    # Handle case where paper details are not found
    return "Paper details not found", 404
