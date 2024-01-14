# data_loader.py
import json
from models.course import Course
from models.semester import Semester
from models.subject import Subject
from models.question_paper import QuestionPaper
from models.question import Question
from models.database import db

def load_data(json_file_path):
    try:
        with open(json_file_path, 'r') as file:
            data = json.load(file)

        for entry in data:
            course_name = entry['Course']
            semesters_data = entry['data']  # 'data' is an array of semesters

            # Insert data into Courses table
            course = Course(CourseName=course_name)
            db.session.add(course)
            db.session.flush()  # This is important to get the auto-incremented ID
            course_id = course.CourseID

            print(f"CourseID: {course_id}")

            for semester_data in semesters_data:
                semester_name, subjects = next(iter(semester_data.items()))

                # Insert data into Semesters table
                semester = Semester(CourseID=course_id, SemesterName=semester_name)
                db.session.add(semester)
                db.session.flush()
                semester_id = semester.SemesterID

                print(f"SemesterID: {semester_id}")

                for subject_data in subjects:
                    code = subject_data['Code']
                    name = subject_data['Name']

                    # Insert data into Subjects table
                    subject = Subject(SemesterID=semester_id, Code=code, SubjectName=name)
                    db.session.add(subject)

                    # Similar logic for other tables

        db.session.commit()
        print("Data loaded successfully.")
    except Exception as e:
        print(f"Error: {e}")
        db.session.rollback()
