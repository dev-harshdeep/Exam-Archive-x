# pdf_upload_bp.py
from flask import Blueprint, render_template, request, jsonify, session , json , current_app
import io
from PIL import Image
import base64
import fitz  # PyMuPDF
from models.subject import Subject
import os
import tempfile
import uuid  # For generating unique filenames
from models.ocr import ocr_image
from models.subject import Subject
from models.question import Question
from models.question_paper import QuestionPaper
from models.database import db
import re

pdf_upload_bp = Blueprint('pdf_upload', __name__)

# Define a temporary directory to store images
TEMP_IMAGE_DIR = 'temp_images/'

# Ensure the temporary directory exists
os.makedirs(TEMP_IMAGE_DIR, exist_ok=True)

def pdf_to_images(pdf_data):
    pdf_document = fitz.open(stream=pdf_data, filetype="pdf")
    images = []

    for page_num in range(pdf_document.page_count):
        page = pdf_document[page_num]
        image_list = page.get_pixmap()
        img = Image.frombytes("RGB", [image_list.width, image_list.height], image_list.samples)
        images.append(img)

    pdf_document.close()
    return images

def stitch_images_vertically(images):
    widths, heights = zip(*(i.size for i in images))
    max_width = max(widths)
    total_height = sum(heights)

    new_image = Image.new('RGB', (max_width, total_height))

    y_offset = 0
    for img in images:
        new_image.paste(img, (0, y_offset))
        y_offset += img.size[1]

    return new_image

@pdf_upload_bp.route('/subjectCodeSuggestions')
def subject_code_suggestions():
    input_text = request.args.get('input', '')
    suggestions = Subject.query.filter(Subject.Code.ilike(f'%{input_text}%')).distinct(Subject.Code).limit(10).all()
    return jsonify([suggestion.Code for suggestion in suggestions])

@pdf_upload_bp.route('/pdfUpload', methods=['GET', 'POST'])
def pdf_upload():
    if request.method == 'POST':
        pdf_file = request.files.get('pdf_file')

        if not pdf_file:
            return "No PDF file provided", 400

        try:
            pdf_data = pdf_file.read()
            pdf_images = pdf_to_images(pdf_data)
            long_image = stitch_images_vertically(pdf_images)

            # Generate a unique filename for the image
            image_filename = str(uuid.uuid4())[:8] + '.png'
            image_path = os.path.join(TEMP_IMAGE_DIR, image_filename)
            # Save the image temporarily on the server
            long_image.save(image_path, format='PNG')

            # Store the image path in the session
            session['image_filename'] = image_filename

            # Trigger the result message in the template
            with open(image_path, 'rb') as image_file:
                encoded_image_data = base64.b64encode(image_file.read()).decode('utf-8')

            return render_template('selectQuestions.html', image_data=encoded_image_data)

        except Exception as e:
            return f"Error processing the PDF file: {str(e)}", 500

    return render_template('pdfUpload.html')

@pdf_upload_bp.route('/saveSelections', methods=['POST'])
def save_selections():
    selections_data = request.json.get('selections', [])

    # Store the new selections in the session
    if selections_data:
        selections_data = selections_data[:-1]  # Remove the last empty selection
        for i, selection in enumerate(selections_data, start=1):
            selection['unit'] = f'Unit {i}'  # Assign default unit based on order

    session['selections'] = selections_data

    # You can perform additional server-side processing here, such as saving the selections or image path to a database

    return jsonify({'message': 'Selections saved successfully'})


def save_selection_as_json(selection):
    # Create a directory to store JSON files if it doesn't exist
    os.makedirs('selections', exist_ok=True)

    # Generate a unique filename for the JSON file
    json_filename = f"{selection['unit']}_selection.json"
    json_filepath = os.path.join('selections', json_filename)

    # Write selection data to JSON file
    with open(json_filepath, 'w') as json_file:
        json.dump(selection, json_file)

# Assuming db is your SQLAlchemy instance
def extract_paper_details(text):
    # Extract year from the text
    year_pattern = r'(?:Jan\.|Feb\.|Mar\.|Apr\.|May|Jun\.|Jul\.|Aug\.|Sep\.|Oct\.|Nov\.|Dec\.)?,?\s*(\d{4})'
    year_match = re.search(year_pattern, text)
    year = year_match.group(1) if year_match else None

    # Get all paper codes from the database
    all_paper_codes = [subject.Code for subject in Subject.query.all()]

    # Variations to check for each paper code
    variations = []
    for code in all_paper_codes:
        if len(code) == 6:
            variations.extend([code, f"{code[:3]}-{code[3:]}"])
        elif len(code) == 7:
            variations.extend([code, code.replace("-", "")])

    # Search for each paper code variation in the text
    found_paper_codes = []
    for variation in variations:
        if variation.lower() in text.lower():
            found_paper_codes.append(variation)

    # Determine paper type based on found paper codes
    if "mid semester" in text.lower():
        paper_type = "mid semester"
    elif "end semester" in text.lower():
        paper_type = "end semester"
    else:
        paper_type = None

    current_app.logger.info("Paper Type:")
    current_app.logger.info(paper_type)
    current_app.logger.info("Year:")
    current_app.logger.info(year)
    current_app.logger.info("Paper Code:")
    current_app.logger.info(found_paper_codes)
    return paper_type, year, found_paper_codes



@pdf_upload_bp.route('/showSelections', methods=['GET'])
def show_selections():
    # Retrieve selections and image data from the session
    selections_data = session.get('selections', [])
    image_filename = session.get('image_filename', '')
    image_path = os.path.join(TEMP_IMAGE_DIR, image_filename)

    # Create a temporary directory to store encoded cropped images
    temp_cropped_dir = tempfile.mkdtemp()
    ocr_data = []
    estimated_details = {'paperType':None,'paperYear':None , 'paperCode':None}
    
    # Process the selections to get cropped images and perform OCR
    for idx, selection in enumerate(selections_data):
        start = selection['start']
        end = selection['end']
        encoded_cropped_image = crop_image(image_path, start, end)
        selection['cropped_image'] = encoded_cropped_image

        # Decode the base64-encoded string back to bytes
        decoded_image_data = base64.b64decode(encoded_cropped_image)

        # Save the decoded image data as a PNG file
        cropped_image_path = os.path.join(temp_cropped_dir, f'{selection["start"]}_{selection["end"]}.png')
        with open(cropped_image_path, 'wb') as f:
            f.write(decoded_image_data)

        # Perform OCR on the saved image file
        ocr_result = ocr_image(cropped_image_path)
        ocr_data.append(ocr_result)
        
        # Log the OCR result
        # current_app.logger.info(ocr_result)

        # You may want to store or process the OCR result here
        
        # For the first selection, extract OCR result from the start coordinate
        if idx == 0:

            start = 0
            end = selection['start']
            encoded_cropped_image = crop_image(image_path, start, end)
          
            decoded_image_data = base64.b64decode(encoded_cropped_image)

            cropped_image_path = os.path.join(temp_cropped_dir, f'{start}_{end}.png')
            with open(cropped_image_path, 'wb') as f:
                f.write(decoded_image_data)

            ocr_result = ocr_image(cropped_image_path)
            
            # Log the OCR result
            current_app.logger.info(ocr_result)
            estimated_details['paperType'] , estimated_details['paperYear'],estimated_details['paperCode']  =extract_paper_details(ocr_result)

            # session['estimated_details'] = estimated_details

    # Pass selections and OCR data to the template
    return render_template('showSelections.html', selections=selections_data, ocr_data=ocr_data ,  paperDetails = estimated_details)


def crop_image(image_path, start, end):
    print(image_path)
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

@pdf_upload_bp.route('/submitSelections', methods=['POST'])
def submit_selections():
    try:
        additional_details = request.json.get('additionalDetails')
        selections_data = request.json.get('selectionsData')
        ocr_data = request.json.get('ocrData')

        # Extract additional details
        subject_code = additional_details.get('subject_code')
        year = additional_details.get('year')
        paper_type = additional_details.get('paper_type')

        # Fetch SubjectID based on subject_code
        subject = Subject.query.filter_by(Code=subject_code).first()
        if subject is None:
            raise ValueError(f"Subject with code {subject_code} not found")

        subject_id = subject.SubjectID

        # Create a new question paper instance
        question_paper = QuestionPaper(SubjectID=subject_id, Year=year, ExamType=paper_type)
        db.session.add(question_paper)
        db.session.commit()

        # Extract selection data and OCR data
        for selection, ocr_text in zip(selections_data, ocr_data):
            start = int(selection['start'])
            end = int(selection['end'])
            units = selection['units']

            # Create a new question instance
            question = Question(PaperID=question_paper.PaperID, QuestionNumber=len(selections_data), Coordinates=f"{start}-{end}", MetaText=ocr_text)
            db.session.add(question)
        image_path = session.get('image_path')

        # Update file path for the question paper
        question_paper.FilePath = image_path
        db.session.commit()

        return jsonify({'message': 'Data submitted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500