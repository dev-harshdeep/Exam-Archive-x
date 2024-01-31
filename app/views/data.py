from flask import Blueprint, jsonify
from models.course import Course
from models.semester import Semester
from models.subject import Subject
from models.question_paper import QuestionPaper
from models.question import Question

data_bp = Blueprint('data', __name__)

@data_bp.route('/structured_data', methods=['GET'])
def get_structured_data():
    structured_data = {}

    # Fetch courses and related data
    courses = Course.query.all()
    for course in courses:
        structured_data[course.CourseName] = {}

        # Fetch semesters for each course
        semesters = Semester.query.filter_by(CourseID=course.CourseID).all()
        for semester in semesters:
            structured_data[course.CourseName][semester.SemesterName] = {}

            # Fetch subjects for each semester
            subjects = Subject.query.filter_by(SemesterID=semester.SemesterID).all()
            for subject in subjects:
                structured_data[course.CourseName][semester.SemesterName][subject.Code] = {}

                # Fetch question papers for each subject
                question_papers = QuestionPaper.query.filter_by(SubjectID=subject.SubjectID).all()
                for paper in question_papers:
                    structured_data[course.CourseName][semester.SemesterName][subject.Code][paper.ExamType] = []

                    # Fetch questions for each paper
                    questions = Question.query.filter_by(PaperID=paper.PaperID).all()
                    for question in questions:
                        structured_data[course.CourseName][semester.SemesterName][subject.Code][paper.ExamType].append({
                            'question_number': question.QuestionNumber,
                            'coordinates': question.Coordinates,
                            'meta_text': question.MetaText
                        })

    return jsonify(structured_data)
