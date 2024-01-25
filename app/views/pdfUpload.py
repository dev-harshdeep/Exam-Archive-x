# pdf_upload_bp.py
from flask import Blueprint, render_template, request, jsonify, session , json
import io
from PIL import Image
import base64
import fitz  # PyMuPDF
import os
import uuid  # For generating unique filenames

pdf_upload_bp = Blueprint('pdf_upload', __name__)

# Define a temporary directory to store images
TEMP_IMAGE_DIR = 'temp_images'

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
            image_filename = str(uuid.uuid4()) + '.png'
            image_path = os.path.join(TEMP_IMAGE_DIR, image_filename)

            # Save the image temporarily on the server
            long_image.save(image_path, format='PNG')

            # Store the image path in the session
            session['image_path'] = image_path

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




@pdf_upload_bp.route('/showSelections', methods=['GET'])
def show_selections():
    # Retrieve selections and image data from the session
    selections_data = session.get('selections', [])
    image_path = session.get('image_path', '')

    # Process the selections to get cropped images
    for selection in selections_data:
        start = selection['start']
        end = selection['end']
        cropped_image = crop_image(image_path, start, end)
        selection['cropped_image'] = cropped_image

    return render_template('showSelections.html', selections=selections_data)

def crop_image(image_path, start, end):
    try:
        # You need to use a proper image processing library to crop the image
        # This is a simplified example using PIL
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

        print("Additional Details:", additional_details)
        print("Selections Data:", selections_data)

        # Perform any additional processing or save data to a database

        return jsonify({'message': 'Data submitted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
