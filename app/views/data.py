# views/data.py

from flask import Blueprint, jsonify
from models.course import Course
from models.subject import Subject
from models.database import db
from sqlalchemy import inspect

data_bp = Blueprint('data', __name__)

@data_bp.route('/tables-info')
def get_tables_info():
    with db.engine.connect() as connection:
        inspector = inspect(connection)

        tables_info = []

        for table_name in inspector.get_table_names():
            columns = inspector.get_columns(table_name)
            table_info = {
                'table_name': table_name,
                'columns': [{'name': column['name'], 'type': str(column['type'])} for column in columns]
            }
            tables_info.append(table_info)

        return jsonify({'tables_info': tables_info})

@data_bp.route('/courses-data')
def get_courses_data():
    courses_data = Course.query.all()
    data = [{'CourseID': course.CourseID, 'CourseName': course.CourseName} for course in courses_data]
    return jsonify({'courses': data})

@data_bp.route('/subject-data')
def get_subject_data():
    subject_data = Subject.query.all()
    data = [{'SubjectID': subject.SubjectID, 'Code': subject.Code, 'SubjectName': subject.SubjectName} for subject in subject_data]
    return jsonify({'subjects': data})

