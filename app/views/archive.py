from flask import Blueprint, render_template, url_for
from models.course import Course
from models.semester import Semester
from models.subject import Subject
from models.question_paper import QuestionPaper
from models.subject_semester import SubjectSemester
from models.question import Question
Question
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
    course = Course.query.get(course_id)
    semester = Semester.query.get(semester_id)
    subject = Subject.query.get(subject_id)
    paper = QuestionPaper.query.get(paper_id)
    
    # Fetch questions belonging to the paper
    questions = Question.query.filter_by(PaperID=paper_id).all()
    
    return render_template('paper_details.html', course=course, semester=semester, subject=subject, paper=paper, questions=questions)
