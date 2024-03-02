import os
import base64
import io
from flask import Blueprint, render_template, request, jsonify
from models.question import Question
from models.subject import Subject
from models.question_paper import QuestionPaper
from PIL import Image

search_bp = Blueprint('search_bp', __name__)

def crop_image(image_path, start, end):
    try:
        original_image = Image.open(image_path)

        # Validate dimensions to prevent "tile cannot extend outside image" error
        if start < 0 or end > original_image.height or start >= end:
            raise ValueError("Invalid crop dimensions")

        # Crop the image based on the start and end coordinates
        cropped_image = original_image.crop((0, start, original_image.width, end))

        # Save the cropped image temporarily on the server
        buffered = io.BytesIO()
        cropped_image.save(buffered, format="PNG")
        encoded_cropped_image = base64.b64encode(buffered.getvalue()).decode('utf-8')

        return encoded_cropped_image

    except Exception as e:
        return f"Error cropping the image: {str(e)}"
@search_bp.route('/search', methods=['GET'])
def search():
    query = request.args.get('query').strip().lower()
    page = int(request.args.get('page', 1))  # Default to page 1 if not provided
    results_per_page = int(request.args.get('results_per_page', 10))  # Default to 10 results per page

    if not query:
        return jsonify({'error': 'No query provided'}), 400

    # Calculate offset for pagination
    offset = (page - 1) * results_per_page

    # Perform database query with pagination
    question_results = Question.query.filter(Question.MetaText.ilike(f'%{query}%')).offset(offset).limit(results_per_page).all()

    # Get total number of results for pagination
    total_results = Question.query.filter(Question.MetaText.ilike(f'%{query}%')).count()
    total_pages = (total_results + results_per_page - 1) // results_per_page

    # Format the results
    formatted_results = []

    for result in question_results:
        paper = QuestionPaper.query.filter_by(PaperID=result.PaperID).first()
        subject = Subject.query.filter_by(SubjectID=paper.SubjectID).first()

        image_path = paper.FilePath
        cropped_image_data = crop_image(image_path, int(result.Coordinates.split('-')[0]), int(result.Coordinates.split('-')[1]))

        formatted_results.append({
            'question_id': result.QuestionID,
            'paper_id': result.PaperID,
            'question_number': result.QuestionNumber,
            'coordinates': result.Coordinates,
            'meta_text': result.MetaText,
            'year': paper.Year,
            'exam_type': paper.ExamType,
            'file_path': paper.FilePath,
            'image_data': cropped_image_data,
            'subject_code': subject.Code,
            'subject_name': subject.SubjectName
        })

    return jsonify({'results': formatted_results, 'total_pages': total_pages})


@search_bp.route('/search/suggestions', methods=['GET'])
def suggestions():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'No query provided'}), 400

    # Get suggestions from database based on the query
    suggestions = Question.query.filter(Question.MetaText.ilike(f'%{query}%')).limit(5).all()
    suggestions = [question.MetaText for question in suggestions]

    return jsonify({'suggestions': suggestions})

@search_bp.route('/search_page')
def search_page():
    query = request.args.get('query')  # Get the query parameter from the URL
    return render_template('search_page.html', query=query)

