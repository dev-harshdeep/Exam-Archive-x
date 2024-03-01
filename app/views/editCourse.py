from flask import Blueprint, render_template,request,jsonify,current_app
from flask import request
from models.course import Course
from models.semester import Semester
from models.subject import Subject
from models.subject_semester import SubjectSemester
from models.database import db
# Create a blueprint instance
edit_course_bp = Blueprint('edit_course', __name__)

# Define a route for the root URL '/'
@edit_course_bp.route('/')
def index():
    # Render the index.html template
    return render_template('edit-course.html')
@edit_course_bp.route('/backend_endpoint', methods=['POST'])
def handle_form_data():
    data = request.json
    if data:
        course_name = data.get('courseName')
        num_semesters = data.get('numSemesters')
        all_semesters_data = data.get('allSemestersData')

        # Create a new course object and add it to the database
        course = Course(CourseName=course_name)
        db.session.add(course)
        db.session.commit()

        # Iterate over all semester data and create semester and subject objects
        for semester_data in all_semesters_data:
            semester_name = semester_data.get('name')
            subjects_data = semester_data.get('subjects')

            # Create a new semester object and associate it with the course
            semester = Semester(CourseID=course.CourseID, SemesterName=semester_name)
            db.session.add(semester)
            db.session.commit()

            # Iterate over subjects data and create subject objects
            for subject_data in subjects_data:
                subject_name = subject_data.get('name')
                subject_code = subject_data.get('code')

                # Create a new subject object
                subject = Subject(Code=subject_code, SubjectName=subject_name)
                db.session.add(subject)
                db.session.commit()

                # Associate the subject with the semester
                subject_semester = SubjectSemester(SubjectID=subject.SubjectID, SemesterID=semester.SemesterID)
                db.session.add(subject_semester)
                db.session.commit()

        return jsonify({"message": "Data received and saved successfully"}), 200
    else:
        return jsonify({"error": "No data received"}), 400