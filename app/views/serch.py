# app/search_bp.py

from flask import Blueprint, render_template, request, jsonify 
from models.question import Question
from models.subject import Subject
from models.question_paper import QuestionPaper

search_bp = Blueprint('search_bp', __name__)

@search_bp.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'No query provided'}), 400

    # Search in meta text of Questions
    query = request.args.get('query').strip().lower()
    question_results = Question.query.filter(Question.MetaText.ilike(f'%{query}%')).all()
    # Format the results
    formatted_results = []

    for result in question_results:
        paper = QuestionPaper.query.filter_by(PaperID=result.PaperID).first()
        subject = Subject.query.filter_by(SubjectID=paper.SubjectID).first()
        
        formatted_results.append({
            'question_id': result.QuestionID,
            'paper_id': result.PaperID,
            'question_number': result.QuestionNumber,
            'coordinates': result.Coordinates,
            'meta_text': result.MetaText,
            'year': paper.Year,
            'exam_type': paper.ExamType,
            'file_path': paper.FilePath,
            'subject_code': subject.Code,
            'subject_name': subject.SubjectName
            # Add more details as needed
        })

    return jsonify({'results': formatted_results})

@search_bp.route('/search/suggestions', methods=['GET'])
def suggestions():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'No query provided'}), 400

    # Get suggestions from database based on the query
    # Example: You can use LIKE query to find similar terms in your database
    suggestions = []

    return jsonify({'suggestions': suggestions})

@search_bp.route('/search_page')
def search_page():
    return render_template('search_page.html')
